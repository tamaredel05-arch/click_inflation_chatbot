"""
DB Tools - BigQuery SQL Execution with Caching
================================================
Tools for executing SQL on BigQuery with built-in caching mechanism.

This module provides:
1. run_sql_tool - main tool for executing SQL queries
2. Automatic caching mechanism for repeated queries
3. Lazy connection to BigQuery (created only on first use)

Performance improvements:
- Caching saves repeated calls to BigQuery
- Cache Agent was removed - caching is performed here directly
"""

import sys
from pathlib import Path

# =============================================================================
# Add project path to Python path
# =============================================================================
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import time
from typing import Dict, List, Any
from pydantic import BaseModel

from agents.cache_sql.tools import (
    is_cacheable_impl as is_cacheable,
    normalize_sql,
    normalize_question,
    TTL_SECONDS,
    get_global_cache_state,
    IsCacheableInput
)
from agents.db.bq_client import BQClient


# =============================================================================
# Input Schema for Tool
# =============================================================================

class RunSQLInput(BaseModel):
    """
    Input model for SQL execution tool.
    
    Attributes:
        sql: SQL query to execute on BigQuery
        final_question: User's original question (optional, for question-level caching)
    """
    sql: str
    final_question: str = None  # Optional - for question-level caching


# =============================================================================
# Lazy Connection to BigQuery
# =============================================================================

# Global instance - created only on first use (lazy initialization)
_bq_instance = None


def get_bq() -> BQClient:
    """
    Returns a BigQuery client instance.
    
    Uses lazy initialization to not create a connection
    until actually needed (saves loading time).
    
    Returns:
        BQClient: Ready-to-use instance
    """
    global _bq_instance
    if _bq_instance is None:
        _bq_instance = BQClient()
    return _bq_instance


# =============================================================================
# Main SQL Execution Function
# =============================================================================

def run_sql(input: RunSQLInput, tool_context=None) -> Dict[str, Any]:
    """
    Executes SQL query on BigQuery with two-layer caching support.
    
    Workflow (two-layer cache):
    1. Check question-level cache (if final_question exists)
    2. Check SQL-level cache (fallback)
    3. If not found - execute on BigQuery and save to both caches
    
    Advantage of two-layer cache:
    - Identical question always returns same result (even if SQL slightly differs)
    - Identical SQL is also saved (for future use)
    
    Args:
        input: Model with SQL query and final_question (optional)
        tool_context: Tool context (not currently used)
    
    Returns:
        Dict with:
        - sql: The executed query
        - rows: Results list
        - summary: Summary (how many rows)
        - from_cache: Whether the result is from cache
    """
    # Get global cache state
    cache_state = get_global_cache_state()
    sql = input.sql
    final_question = input.final_question
    
    # Normalize the keys
    normalized_sql = normalize_sql(sql)
    normalized_q = normalize_question(final_question) if final_question else None
    
    now = time.time()

    # ===================
    # Step 1: Check Question-Level Cache (preferred!)
    # ===================
    if normalized_q:
        # Check TTL for question - if expired, delete safely
        if normalized_q in cache_state.question_ttl:
            if now - cache_state.question_ttl[normalized_q] > TTL_SECONDS:
                # Expired - delete safely (pop prevents KeyError)
                cache_state.question_cache.pop(normalized_q, None)
                cache_state.question_ttl.pop(normalized_q, None)
                print(f"[CACHE] ⏰ Cache expired for question: {final_question[:50]}...")
        
        # Check if question is in cache
        if normalized_q in cache_state.question_cache:
            cached_result = cache_state.question_cache[normalized_q]
            print(f"[CACHE HIT] ✅ Question found in cache: {final_question[:60]}...")
            print(f"[CACHE DEBUG] Question key: {normalized_q[:60]}...")
            return {
                "sql": sql,
                "rows": cached_result["rows"],
                "summary": f"Query returned {len(cached_result['rows'])} rows",
                "from_cache": True
            }

    # ===================
    # Step 2: Check SQL-Level Cache (fallback)
    # ===================
    # Check TTL for SQL - if expired, delete safely
    if normalized_sql in cache_state.ttl:
        if now - cache_state.ttl[normalized_sql] > TTL_SECONDS:
            # Expired - delete safely (pop prevents KeyError)
            cache_state.cache.pop(normalized_sql, None)
            cache_state.ttl.pop(normalized_sql, None)
            print(f"[CACHE] ⏰ Cache expired for SQL")
    
    if normalized_sql in cache_state.cache:
        # Found query in SQL cache - return result immediately
        print(f"[CACHE HIT] ✅ SQL found in cache: {sql[:60]}...")
        print(f"[CACHE DEBUG] SQL key: {normalized_sql[:60]}...")
        return {
            "sql": sql,
            "rows": cache_state.cache[normalized_sql]["rows"],
            "summary": f"Query returned {len(cache_state.cache[normalized_sql]['rows'])} rows",
            "from_cache": True
        }

    # ===================
    # Step 3: Cache MISS - Execute on BigQuery
    # ===================
    print(f"[CACHE MISS] 🔄 Executing new query on BigQuery: {sql[:60]}...")
    if final_question:
        print(f"[CACHE DEBUG] Question: {final_question[:60]}...")
        print(f"[CACHE DEBUG] Question key (normalized): {normalized_q[:60] if normalized_q else 'N/A'}...")
    print(f"[CACHE DEBUG] SQL key (normalized): {normalized_sql[:60]}...")
    
    result_iter = get_bq().execute_query(sql, "agent_query")
    rows = [dict(row) for row in result_iter]

    result = {
        "sql": sql,
        "rows": rows,
        "summary": f"Query returned {len(rows)} rows",
        "from_cache": False
    }

    # ===================
    # Step 4: Save to cache (both layers) if possible
    # ===================
    if is_cacheable(IsCacheableInput(sql=sql)):
        # Save to SQL cache
        cache_state.cache[normalized_sql] = result
        cache_state.ttl[normalized_sql] = now
        print(f"[CACHE] 💾 Saved to SQL cache: {normalized_sql[:60]}...")
        
        # Save to question cache (if exists)
        if normalized_q:
            cache_state.question_cache[normalized_q] = result
            cache_state.question_ttl[normalized_q] = now
            print(f"[CACHE] 💾 Saved to question cache: {normalized_q[:60]}...")
    else:
        print(f"[CACHE] ⏭️ Query not cacheable (relative date or LIMIT)")

    return result


# =============================================================================
# Wrapper for use by Agent
# =============================================================================

def run_sql_tool(input: RunSQLInput, tool_context=None) -> Dict[str, Any]:
    """
    Wrapper function for use as ADK Agent tool.
    
    The Agent expects a function named run_sql_tool.
    This is a simple wrapper function that calls run_sql.
    
    Args:
        input: Model with SQL query and final_question (optional)
        tool_context: Tool context from ADK
    
    Returns:
        Dict with query results
    """
    return run_sql(input, tool_context)