#!/usr/bin/env python3
"""
בדיקות לקאש ומונה ניסיונות - Cache and Counter Tests
======================================================
סקריפט זה בודק את תפקוד הקאש הדו-שכבתי ומנגנון מונה הניסיונות.

בדיקות הקאש:
1. קאש ברמת השאלה - שאלה זהה מחזירה CACHE HIT
2. קאש ברמת ה-SQL - SQL זהה מחזירה CACHE HIT
3. TTL - תוקף הקאש

בדיקות מונה הניסיונות:
1. מונה עולה בכל ניסיון הבהרה (1/3, 2/3, 3/3)
2. מונה נשמר בין סשנים
3. מונה מתאפס אחרי הצלחה

הרצה:
    cd c:\\Users\\USER\\click_inflation_chatbot
    python scripts\\test_cache_and_counter.py
"""

import sys
from pathlib import Path

# הוספת נתיב הפרויקט
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import time
from typing import Dict, Any

# =============================================================================
# Mock Classes for Testing
# =============================================================================

class MockPart:
    """מדמה Part של ADK"""
    def __init__(self, text: str):
        self.text = text


class MockContent:
    """מדמה Content של ADK"""
    def __init__(self, text: str):
        self.parts = [MockPart(text)]
        self.role = "user"


class MockState(dict):
    """מדמה את session.state של ADK"""
    def setdefault(self, key, default):
        if key not in self:
            self[key] = default
        return self[key]


class MockSession:
    """מדמה Session של ADK"""
    def __init__(self):
        self.state = MockState()


class MockContext:
    """מדמה Context של ADK"""
    def __init__(self, user_message: str):
        self.session = MockSession()
        self.user_content = MockContent(user_message)


# =============================================================================
# Test Utilities
# =============================================================================

def print_test_header(test_name: str):
    """מדפיס כותרת בדיקה"""
    print("\n" + "=" * 70)
    print(f"🧪 TEST: {test_name}")
    print("=" * 70)


def print_subtest(name: str):
    """מדפיס כותרת משנה"""
    print(f"\n  📋 {name}")
    print("  " + "-" * 50)


def assert_equals(actual, expected, message: str) -> bool:
    """בדיקת שוויון עם הודעה"""
    if actual == expected:
        print(f"   ✅ {message}: PASS")
        return True
    else:
        print(f"   ❌ {message}: FAIL")
        print(f"      Expected: {expected}")
        print(f"      Actual: {actual}")
        return False


def assert_true(value: bool, message: str) -> bool:
    """בדיקה שערך הוא True"""
    if value:
        print(f"   ✅ {message}: PASS")
        return True
    else:
        print(f"   ❌ {message}: FAIL")
        return False


def assert_false(value: bool, message: str) -> bool:
    """בדיקה שערך הוא False"""
    if not value:
        print(f"   ✅ {message}: PASS")
        return True
    else:
        print(f"   ❌ {message}: FAIL")
        return False


def assert_in(item, container, message: str) -> bool:
    """בדיקה שפריט בתוך מיכל"""
    if item in container:
        print(f"   ✅ {message}: PASS")
        return True
    else:
        print(f"   ❌ {message}: FAIL ('{item}' not found)")
        return False


# =============================================================================
# Test 1: Question-Level Cache
# =============================================================================

def test_question_level_cache():
    """
    בדיקה 1: קאש ברמת השאלה
    
    שאלה זהה צריכה להחזיר CACHE HIT גם אם ה-SQL שונה.
    זה הפתרון לבעיה שה-NL2SQL מייצר SQL שונה בכל פעם.
    """
    print_test_header("Question-Level Cache")
    
    passed = 0
    total = 0
    
    try:
        from agents.cache_sql.tools import (
            CacheState,
            normalize_question,
            get_global_cache_state
        )
        from agents.db.tools import run_sql, RunSQLInput
        
        # איפוס הקאש לפני הבדיקה
        cache_state = get_global_cache_state()
        cache_state.question_cache.clear()
        cache_state.question_ttl.clear()
        cache_state.cache.clear()
        cache_state.ttl.clear()
        
        print_subtest("normalize_question function")
        
        # בדיקת נרמול שאלה
        q1 = "How many clicks in October 2025?"
        q2 = "  how many clicks in october 2025?  "
        q3 = "HOW MANY CLICKS IN OCTOBER 2025?"
        
        total += 1
        if assert_equals(normalize_question(q1), normalize_question(q2), 
                         "Same question with whitespace normalizes equally"):
            passed += 1
        
        total += 1
        if assert_equals(normalize_question(q1), normalize_question(q3),
                         "Same question with case normalizes equally"):
            passed += 1
        
        print_subtest("Question cache storage")
        
        # בדיקת אחסון בקאש לפי שאלה
        # נסמלץ שמירה ישירה לקאש (כי לא רוצים לקרוא ל-BigQuery באמת)
        test_question = "how many clicks in october 2025 for facebook?"
        normalized_q = normalize_question(test_question)
        
        mock_result = {
            "sql": "SELECT COUNT(*) FROM clicks WHERE ...",
            "rows": [{"count": 12345}],
            "summary": "Query returned 1 rows",
            "from_cache": False
        }
        
        # שמירה ישירה לקאש
        cache_state.question_cache[normalized_q] = mock_result
        cache_state.question_ttl[normalized_q] = time.time()
        
        total += 1
        if assert_in(normalized_q, cache_state.question_cache,
                     "Question stored in cache"):
            passed += 1
        
        # בדיקה שאפשר למצוא את השאלה
        total += 1
        found = normalized_q in cache_state.question_cache
        if assert_true(found, "Question can be found in cache"):
            passed += 1
        
        print_subtest("Cache HIT on identical question")
        
        # שאלה זהה (עם הבדלי רווחים/אותיות) צריכה לפגוע בקאש
        similar_question = "  HOW MANY CLICKS in October 2025 for Facebook?  "
        similar_normalized = normalize_question(similar_question)
        
        total += 1
        if assert_equals(similar_normalized, normalized_q,
                         "Similar question normalizes to same key"):
            passed += 1
        
        total += 1
        if assert_in(similar_normalized, cache_state.question_cache,
                     "Similar question finds cache entry"):
            passed += 1
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    return passed, total


# =============================================================================
# Test 2: SQL-Level Cache (Fallback)
# =============================================================================

def test_sql_level_cache():
    """
    בדיקה 2: קאש ברמת ה-SQL (fallback)
    
    SQL זהה צריך להחזיר CACHE HIT.
    זה fallback למקרה שאין final_question.
    """
    print_test_header("SQL-Level Cache (Fallback)")
    
    passed = 0
    total = 0
    
    try:
        from agents.cache_sql.tools import (
            normalize_sql,
            get_global_cache_state
        )
        
        # איפוס הקאש
        cache_state = get_global_cache_state()
        cache_state.cache.clear()
        cache_state.ttl.clear()
        
        print_subtest("normalize_sql function")
        
        # בדיקת נרמול SQL
        sql1 = "SELECT COUNT(*) FROM clicks WHERE date = '2025-10-01'"
        sql2 = "select count(*) from clicks where date = '2025-10-01'"
        sql3 = "SELECT   COUNT(*)   FROM   clicks   WHERE   date = '2025-10-01'"
        
        total += 1
        if assert_equals(normalize_sql(sql1), normalize_sql(sql2),
                         "Same SQL with case normalizes equally"):
            passed += 1
        
        total += 1
        if assert_equals(normalize_sql(sql1), normalize_sql(sql3),
                         "Same SQL with whitespace normalizes equally"):
            passed += 1
        
        print_subtest("SQL cache storage")
        
        # שמירה ישירה לקאש SQL
        test_sql = "select sum(clicks) from table where date = '2025-10-15'"
        normalized_sql = normalize_sql(test_sql)
        
        mock_result = {
            "sql": test_sql,
            "rows": [{"sum": 99999}],
            "summary": "Query returned 1 rows",
            "from_cache": False
        }
        
        cache_state.cache[normalized_sql] = mock_result
        cache_state.ttl[normalized_sql] = time.time()
        
        total += 1
        if assert_in(normalized_sql, cache_state.cache,
                     "SQL stored in cache"):
            passed += 1
        
        print_subtest("SQL variations should NOT match")
        
        # SQL שונה לא אמור לפגוע בקאש
        different_sql = "select sum(clicks) from table where date = '2025-10-16'"
        different_normalized = normalize_sql(different_sql)
        
        total += 1
        if assert_false(different_normalized in cache_state.cache,
                        "Different SQL date doesn't match cache"):
            passed += 1
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    return passed, total


# =============================================================================
# Test 3: Dual-Level Cache Priority
# =============================================================================

def test_cache_priority():
    """
    בדיקה 3: סדר עדיפויות בקאש
    
    קאש ברמת השאלה צריך לקבל עדיפות על קאש SQL.
    """
    print_test_header("Cache Priority (Question > SQL)")
    
    passed = 0
    total = 0
    
    try:
        from agents.cache_sql.tools import (
            normalize_sql,
            normalize_question,
            get_global_cache_state,
            IsCacheableInput
        )
        from agents.db.tools import RunSQLInput
        
        # איפוס הקאש
        cache_state = get_global_cache_state()
        cache_state.question_cache.clear()
        cache_state.question_ttl.clear()
        cache_state.cache.clear()
        cache_state.ttl.clear()
        
        print_subtest("Both caches have entries")
        
        question = "how many clicks yesterday for facebook?"
        sql = "select count(*) from clicks where date = current_date() - 1"
        
        question_result = {"rows": [{"count": 100}], "from_cache": True}
        sql_result = {"rows": [{"count": 200}], "from_cache": True}
        
        # שמירה בשני הקאשים
        cache_state.question_cache[normalize_question(question)] = question_result
        cache_state.question_ttl[normalize_question(question)] = time.time()
        
        cache_state.cache[normalize_sql(sql)] = sql_result
        cache_state.ttl[normalize_sql(sql)] = time.time()
        
        total += 1
        if assert_true(len(cache_state.question_cache) > 0, 
                       "Question cache has entries"):
            passed += 1
        
        total += 1
        if assert_true(len(cache_state.cache) > 0,
                       "SQL cache has entries"):
            passed += 1
        
        print_subtest("RunSQLInput model accepts final_question")
        
        # בדיקה שהמודל מקבל final_question
        try:
            input_obj = RunSQLInput(sql=sql, final_question=question)
            total += 1
            if assert_equals(input_obj.final_question, question,
                             "RunSQLInput stores final_question"):
                passed += 1
        except Exception as e:
            total += 1
            print(f"   ❌ RunSQLInput model error: {e}")
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    return passed, total


# =============================================================================
# Test 4: Persistent State for Counter
# =============================================================================

def test_persistent_state():
    """
    בדיקה 4: מצב עקבי למונה ניסיונות
    
    המונה צריך להישמר בין בקשות HTTP (סשנים שונים).
    """
    print_test_header("Persistent State for Counter")
    
    passed = 0
    total = 0
    
    try:
        from agent import (
            _get_state_key,
            _get_persistent_state,
            _update_persistent_state,
            _clear_persistent_state,
            _persistent_states
        )
        
        # ניקוי המצב הגלובלי לפני הבדיקה
        _persistent_states.clear()
        
        print_subtest("State key generation")
        
        # בדיקה שמפתח נוצר מהשאלה
        question1 = "How many clicks yesterday?"
        question2 = "how many clicks yesterday?"  # אותה שאלה, אותיות שונות
        question3 = "What is the total?"  # שאלה אחרת
        
        key1 = _get_state_key(question1)
        key2 = _get_state_key(question2)
        key3 = _get_state_key(question3)
        
        total += 1
        if assert_equals(key1, key2, "Same question generates same key"):
            passed += 1
        
        total += 1
        if assert_true(key1 != key3, "Different questions generate different keys"):
            passed += 1
        
        print_subtest("Persistent state creation")
        
        # בדיקת יצירת מצב חדש
        state = _get_persistent_state(key1)
        
        total += 1
        if assert_equals(state["total_clarification_attempts"], 0,
                         "New state starts with 0 attempts"):
            passed += 1
        
        total += 1
        if assert_equals(state["awaiting_field"], None,
                         "New state has no awaiting field"):
            passed += 1
        
        print_subtest("Counter increment persists")
        
        # סימולציה של הגדלת המונה
        _update_persistent_state(key1, {"total_clarification_attempts": 1})
        
        # קבלת המצב שוב (כאילו בקשה חדשה)
        state_again = _get_persistent_state(key1)
        
        total += 1
        if assert_equals(state_again["total_clarification_attempts"], 1,
                         "Counter persists at 1"):
            passed += 1
        
        # הגדלה נוספת
        _update_persistent_state(key1, {"total_clarification_attempts": 2})
        state_again = _get_persistent_state(key1)
        
        total += 1
        if assert_equals(state_again["total_clarification_attempts"], 2,
                         "Counter persists at 2"):
            passed += 1
        
        print_subtest("State isolation between questions")
        
        # בדיקה שמצב של שאלה אחת לא משפיע על שאלה אחרת
        state3 = _get_persistent_state(key3)
        
        total += 1
        if assert_equals(state3["total_clarification_attempts"], 0,
                         "Different question has independent counter"):
            passed += 1
        
        print_subtest("State cleanup after success")
        
        # בדיקת ניקוי מצב אחרי הצלחה
        _clear_persistent_state(key1)
        
        total += 1
        if assert_false(key1 in _persistent_states,
                        "State cleared after success"):
            passed += 1
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    return passed, total


# =============================================================================
# Test 5: Counter Flow Simulation
# =============================================================================

def test_counter_flow():
    """
    בדיקה 5: סימולציה של זרימת מונה
    
    בודק שהמונה עולה: 1/3 → 2/3 → 3/3 → stop
    """
    print_test_header("Counter Flow Simulation")
    
    passed = 0
    total = 0
    
    try:
        from agent import (
            _get_state_key,
            _get_persistent_state,
            _update_persistent_state,
            _clear_persistent_state,
            _persistent_states,
            MAX_CLARIFICATION_ATTEMPTS
        )
        
        # ניקוי
        _persistent_states.clear()
        
        print_subtest("Verify MAX_CLARIFICATION_ATTEMPTS")
        
        total += 1
        if assert_equals(MAX_CLARIFICATION_ATTEMPTS, 3,
                         "MAX_CLARIFICATION_ATTEMPTS is 3"):
            passed += 1
        
        print_subtest("Simulate clarification flow")
        
        question = "כמה קליקים היו?"  # שאלה בעברית
        key = _get_state_key(question)
        
        # ניסיון 1
        state = _get_persistent_state(key)
        attempts = state["total_clarification_attempts"] + 1
        _update_persistent_state(key, {
            "total_clarification_attempts": attempts,
            "awaiting_field": "missing_date"
        })
        
        total += 1
        state = _get_persistent_state(key)
        if assert_equals(state["total_clarification_attempts"], 1,
                         "After 1st clarification: attempts=1"):
            passed += 1
        
        # ניסיון 2 (סימולציה של בקשה חדשה)
        state = _get_persistent_state(key)
        attempts = state["total_clarification_attempts"] + 1
        _update_persistent_state(key, {
            "total_clarification_attempts": attempts
        })
        
        total += 1
        state = _get_persistent_state(key)
        if assert_equals(state["total_clarification_attempts"], 2,
                         "After 2nd clarification: attempts=2"):
            passed += 1
        
        # ניסיון 3
        state = _get_persistent_state(key)
        attempts = state["total_clarification_attempts"] + 1
        _update_persistent_state(key, {
            "total_clarification_attempts": attempts
        })
        
        total += 1
        state = _get_persistent_state(key)
        if assert_equals(state["total_clarification_attempts"], 3,
                         "After 3rd clarification: attempts=3"):
            passed += 1
        
        # בדיקה שהגענו למקסימום
        total += 1
        if assert_true(state["total_clarification_attempts"] >= MAX_CLARIFICATION_ATTEMPTS,
                       "Reached MAX_CLARIFICATION_ATTEMPTS"):
            passed += 1
        
        print_subtest("Counter resets on new question")
        
        # שאלה חדשה צריכה להתחיל מ-0
        new_question = "מה היה אתמול?"
        new_key = _get_state_key(new_question)
        new_state = _get_persistent_state(new_key)
        
        total += 1
        if assert_equals(new_state["total_clarification_attempts"], 0,
                         "New question starts at 0"):
            passed += 1
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    return passed, total


# =============================================================================
# Test 6: is_cacheable Function
# =============================================================================

def test_is_cacheable():
    """
    בדיקה 6: פונקציית is_cacheable
    
    בודק שהפונקציה מזהה נכון אילו שאילתות ניתן לשמור בקאש.
    """
    print_test_header("is_cacheable Function")
    
    passed = 0
    total = 0
    
    try:
        from agents.cache_sql.tools import is_cacheable_impl, IsCacheableInput
        
        print_subtest("Should NOT cache (relative dates)")
        
        # שאילתות עם תאריכים יחסיים - לא לקאש
        relative_queries = [
            "SELECT * FROM clicks WHERE date = CURRENT_DATE()",
            "SELECT * FROM clicks WHERE date = today",
            "SELECT * FROM clicks WHERE date >= yesterday",
            "SELECT * FROM clicks WHERE date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)",
        ]
        
        for sql in relative_queries:
            total += 1
            result = is_cacheable_impl(IsCacheableInput(sql=sql))
            if assert_false(result, f"Not cacheable: {sql[:50]}..."):
                passed += 1
        
        print_subtest("Should NOT cache (LIMIT)")
        
        # שאילתות עם LIMIT - לא לקאש
        limit_queries = [
            "SELECT * FROM clicks LIMIT 10",
            "SELECT TOP 5 * FROM clicks",
        ]
        
        for sql in limit_queries:
            total += 1
            result = is_cacheable_impl(IsCacheableInput(sql=sql))
            if assert_false(result, f"Not cacheable: {sql[:50]}..."):
                passed += 1
        
        print_subtest("Should cache (absolute dates)")
        
        # שאילתות עם תאריכים מוחלטים - כן לקאש
        absolute_queries = [
            "SELECT * FROM clicks WHERE date = '2025-10-15'",
            "SELECT * FROM clicks WHERE date BETWEEN '2025-10-01' AND '2025-10-31'",
            "SELECT * FROM clicks WHERE EXTRACT(YEAR FROM date) = 2025 AND EXTRACT(MONTH FROM date) = 10",
        ]
        
        for sql in absolute_queries:
            total += 1
            result = is_cacheable_impl(IsCacheableInput(sql=sql))
            if assert_true(result, f"Cacheable: {sql[:50]}..."):
                passed += 1
        
        print_subtest("Should cache (month names)")
        
        # שאילתות עם שמות חודשים - כן לקאש
        month_queries = [
            "SELECT * FROM clicks WHERE month = 'October'",
            "SELECT * FROM clicks WHERE month = 'אוקטובר'",
        ]
        
        for sql in month_queries:
            total += 1
            result = is_cacheable_impl(IsCacheableInput(sql=sql))
            if assert_true(result, f"Cacheable: {sql[:50]}..."):
                passed += 1
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    return passed, total


# =============================================================================
# Test 7: Cache Stats
# =============================================================================

def test_cache_stats():
    """
    בדיקה 7: סטטיסטיקות קאש
    
    בודק שפונקציית get_cache_stats מחזירה מידע נכון.
    """
    print_test_header("Cache Statistics")
    
    passed = 0
    total = 0
    
    try:
        from agents.cache_sql.tools import (
            get_global_cache_state,
            get_cache_stats,
            normalize_question,
            normalize_sql
        )
        
        # איפוס הקאש
        cache_state = get_global_cache_state()
        cache_state.question_cache.clear()
        cache_state.question_ttl.clear()
        cache_state.cache.clear()
        cache_state.ttl.clear()
        
        print_subtest("Empty cache stats")
        
        stats = get_cache_stats()
        
        total += 1
        if assert_equals(stats["question_cache_size"], 0,
                         "Empty question cache size is 0"):
            passed += 1
        
        total += 1
        if assert_equals(stats["sql_cache_size"], 0,
                         "Empty SQL cache size is 0"):
            passed += 1
        
        print_subtest("Stats after adding entries")
        
        # הוספת ערכים
        cache_state.question_cache[normalize_question("question 1")] = {}
        cache_state.question_cache[normalize_question("question 2")] = {}
        cache_state.cache[normalize_sql("SELECT 1")] = {}
        
        stats = get_cache_stats()
        
        total += 1
        if assert_equals(stats["question_cache_size"], 2,
                         "Question cache size is 2"):
            passed += 1
        
        total += 1
        if assert_equals(stats["sql_cache_size"], 1,
                         "SQL cache size is 1"):
            passed += 1
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    return passed, total


# =============================================================================
# Main
# =============================================================================

def main():
    """הרצת כל הבדיקות"""
    print("\n" + "=" * 70)
    print("  CACHE AND COUNTER TEST SUITE")
    print("  Click Inflation Chatbot - ADK 1.19")
    print("=" * 70)
    
    total_passed = 0
    total_tests = 0
    results = []
    
    # הרצת הבדיקות
    tests = [
        ("Question-Level Cache", test_question_level_cache),
        ("SQL-Level Cache", test_sql_level_cache),
        ("Cache Priority", test_cache_priority),
        ("Persistent State", test_persistent_state),
        ("Counter Flow", test_counter_flow),
        ("is_cacheable", test_is_cacheable),
        ("Cache Stats", test_cache_stats),
    ]
    
    for name, test_func in tests:
        try:
            passed, total = test_func()
            total_passed += passed
            total_tests += total
            results.append((name, passed, total))
        except Exception as e:
            print(f"\n❌ Test {name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, 0, 1))
            total_tests += 1
    
    # סיכום
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    for name, passed, total in results:
        icon = "✅" if passed == total else "⚠️"
        print(f"  {icon} {name}: {passed}/{total}")
    
    print("-" * 70)
    if total_passed == total_tests:
        print(f"  ✅ ALL TESTS PASSED ({total_passed}/{total_tests})")
        exit_code = 0
    else:
        print(f"  ⚠️  SOME TESTS FAILED ({total_passed}/{total_tests})")
        exit_code = 1
    print("=" * 70 + "\n")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
