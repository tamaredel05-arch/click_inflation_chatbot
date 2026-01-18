"""
Cache SQL Tools - SQL Query Caching Tools
==========================================
This module provides tools for SQL query caching.

Functions:
1. Check if query is cacheable (is_cacheable)
2. Search for query in cache (cache_lookup)
3. Manage global cache state

Caching rules:
- Queries with relative dates (today, yesterday) are not cached
- Queries with LIMIT are not cached
- Queries with absolute dates (2025-01-01) are cached

TTL (Time To Live):
- Queries are cached for 180 days
"""

import time
import re
from pydantic import BaseModel


# =============================================================================
# Input/Output Models
# =============================================================================

class IsCacheableInput(BaseModel):
    """Input model for checking cacheability"""
    sql: str


# =============================================================================
# Global Cache State
# =============================================================================

class CacheState:
    """
    Class for managing cache state - two-layer.
    
    Stores two cache levels:
    1. question_cache - cache by normalized question (more stable)
    2. cache - cache by normalized SQL (fallback)
    
    Attributes:
        question_cache: dict {normalized_question: result}
        question_ttl: dict {normalized_question: timestamp}
        cache: dict {normalized_sql: result}
        ttl: dict {normalized_sql: timestamp}
    """
    def __init__(self):
        # Question-level cache - preferred! Same question always returns same result
        self.question_cache = {}  # Cache dict: {normalized_question: result}
        self.question_ttl = {}    # TTL dict: {normalized_question: timestamp}
        
        # SQL-level cache - fallback for identical queries
        self.cache = {}  # Cache dict: {normalized_sql: result}
        self.ttl = {}    # TTL dict: {normalized_sql: timestamp}

# Shared global instance - all agents use the same cache
_global_cache_state = CacheState()


# =============================================================================
# Constants
# =============================================================================

# Keywords for relative dates - queries with these are not cached
RELATIVE_KEYWORDS = [
    "today", "yesterday", "now()", "current_timestamp", "current_date",
    "this month", "this year", "this week", "last month", "last year",
    "last week", "interval", "date_add", "date_sub",
]

# Month names - queries with these are cached
MONTH_KEYWORDS = [
    "january","february","march","april","may","june",
    "july","august","september","october","november","december",
]

# Absolute date patterns - queries with these are cached
DATE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}",    # 2025-01-01
    r"\d{2}/\d{2}/\d{4}",    # 01/01/2025
    r"\d{4}/\d{2}/\d{2}",    # 2025/01/01
    r"\b\d{8}\b",            # 20250101
]

# Cache save time - 180 days in seconds
TTL_SECONDS = 60 * 60 * 24 * 180


# =============================================================================
# Utility Functions
# =============================================================================

def normalize_sql(sql: str) -> str:
    """
    Normalizes SQL query for cache comparison.
    
    Removes extra whitespace and converts to lowercase.
    This allows finding identical queries even if there are whitespace differences.
    
    Args:
        sql: Original SQL query (can be None)
    
    Returns:
        Normalized query, or empty string if input is empty/None
    """
    # Check for empty input - return empty string to prevent errors
    if not sql:
        return ""
    return " ".join(sql.lower().split())


def normalize_question(question: str) -> str:
    """
    Normalizes user question for cache comparison.
    
    Normalization process:
    1. Remove extra whitespace at start and end
    2. Convert to lowercase
    3. Normalize internal whitespace
    
    This allows finding identical questions even if there are slight whitespace differences.
    
    Args:
        question: User's original question
    
    Returns:
        Normalized question for use as cache key
    """
    if not question:
        return ""
    return " ".join(question.lower().strip().split())

# =============================================================================
# Implementation Functions
# =============================================================================

def is_cacheable_impl(input: IsCacheableInput) -> bool:
    """
    Checks if SQL query is cacheable.
    
    Checking rules:
    1. Queries with relative dates (today, yesterday) - not cached
    2. Queries with LIMIT or TOP - not cached (results can change)
    3. Queries with absolute dates - cached
    4. Queries with month names - cached
    
    Args:
        input: Model with SQL query
    
    Returns:
        True if can be cached, False otherwise
    """
    sql = input.sql.lower()

    # Check for relative dates - if exists, cannot cache
    for word in RELATIVE_KEYWORDS:
        if word in sql:
            return False

    # Check for LIMIT/TOP - if exists, cannot cache (results can change)
    if "limit" in sql or re.search(r"\btop\s+\d+", sql):
        return False

    # Check for absolute dates - if exists, can cache
    for pattern in DATE_PATTERNS:
        if re.search(pattern, sql):
            return True

    # Check for month names - if exists, can cache
    for month in MONTH_KEYWORDS:
        if month in sql:
            return True

    # Check for BETWEEN with year - if exists, can cache
    if "between" in sql and re.search(r"\d{4}", sql):
        return True

    # Check for EXTRACT with defined year and month - can cache
    # Supports any column name (event_time, date, etc.)
    if (
        re.search(r"extract\s*\(\s*year\s+from\s+\w+\s*\)\s*=\s*\d{4}", sql)
        and re.search(r"extract\s*\(\s*month\s+from\s+\w+\s*\)\s*=\s*\d{1,2}", sql)
    ):
        return True

    # Default - do not cache
    return False


# =============================================================================
# Cache Helper Functions
# =============================================================================

def get_global_cache_state():
    """
    Returns the global cache state.
    
    Used by db/tools.py for direct cache access
    without requiring a Cache Agent.
    
    Returns:
        CacheState: Global cache instance
    """
    return _global_cache_state


def get_cache_stats() -> dict:
    """
    Returns statistics on cache state.
    
    Useful for monitoring and debugging.
    
    Returns:
        dict with number of items in each cache
    """
    state = _global_cache_state
    return {
        "question_cache_size": len(state.question_cache),
        "sql_cache_size": len(state.cache),
        "question_cache_keys": list(state.question_cache.keys())[:5],  # Only first 5
        "sql_cache_keys": list(state.cache.keys())[:5]  # Only first 5
    }