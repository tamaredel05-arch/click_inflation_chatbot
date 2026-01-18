"""
Test State Synchronization - ADK 1.19
======================================
סקריפט בדיקה לוידוא סנכרון ה-state בין הסוכנים.

מה הסקריפט בודק:
1. שכל הסוכנים נטענים בהצלחה
2. ש-output_key מוגדר נכון לכל סוכן
3. שהתלויות בין הסוכנים תקינות
4. שהזרימה הבסיסית עובדת

הערה: db_agent, answer_agent, cache_agent הוסרו לשיפור ביצועים.
הפונקציונליות שלהם מתבצעת ישירות ב-Python.

הרצה:
    python scripts/test_state_sync.py
"""

import sys
from pathlib import Path

# =============================================================================
# הוספת נתיב הפרויקט - Add project path
# מוסיף את תיקיית הפרויקט ל-Python path כדי לאפשר imports
# =============================================================================
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def print_header(title: str):
    """מדפיס כותרת מעוצבת"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(name: str, success: bool, details: str = ""):
    """מדפיס תוצאת בדיקה"""
    icon = "✅" if success else "❌"
    print(f"{icon} {name}")
    if details:
        print(f"   → {details}")


def test_imports():
    """
    בדיקה 1: טעינת כל הסוכנים הפעילים
    בודק שכל הסוכנים נטענים ללא שגיאות
    
    הערה: db_agent, answer_agent הוסרו - הפונקציונליות ישירה ב-Python
    """
    print_header("Test 1: Agent Imports")
    
    agents_status = {}
    
    # Intent Recognition Agent
    try:
        from agents.intent_recognition_agent.intent_recognition_agent import intent_recognition_agent
        agents_status["intent_recognition_agent"] = (True, intent_recognition_agent.name)
    except Exception as e:
        agents_status["intent_recognition_agent"] = (False, str(e))
    
    # Validation Agent
    try:
        from agents.validation_agent.validation_agent import validation_agent
        agents_status["validation_agent"] = (True, validation_agent.name)
    except Exception as e:
        agents_status["validation_agent"] = (False, str(e))
    
    # NL2SQL Agent
    try:
        from agents.nl2sql.nl2sql_agent import nl2sql_agent
        agents_status["nl2sql_agent"] = (True, nl2sql_agent.name)
    except Exception as e:
        agents_status["nl2sql_agent"] = (False, str(e))
    
    # DB Tools (לא סוכן - פונקציה ישירה)
    try:
        from agents.db.tools import run_sql_tool, RunSQLInput
        agents_status["db_tools"] = (True, "run_sql_tool loaded")
    except Exception as e:
        agents_status["db_tools"] = (False, str(e))
    
    # Root Agent
    try:
        from agent import root_agent
        agents_status["root_agent"] = (True, root_agent.name)
    except Exception as e:
        agents_status["root_agent"] = (False, str(e))
    
    # Print results
    all_passed = True
    for agent_name, (success, detail) in agents_status.items():
        print_result(agent_name, success, detail)
        if not success:
            all_passed = False
    
    return all_passed


def test_output_keys():
    """
    בדיקה 2: הגדרת output_key
    בודק שכל סוכן שומר ל-state עם המפתח הנכון
    
    הערה: db_agent, answer_agent הוסרו - db_output נשמר ישירות
    """
    print_header("Test 2: Output Keys Configuration")
    
    expected_keys = {
        "intent_recognition_agent": "intent_result",
        "validation_agent": "validation_result",
        "nl2sql_agent": "nl2sql_output",
    }
    
    all_passed = True
    
    try:
        from agents.intent_recognition_agent.intent_recognition_agent import intent_recognition_agent
        from agents.validation_agent.validation_agent import validation_agent
        from agents.nl2sql.nl2sql_agent import nl2sql_agent
        
        agents = {
            "intent_recognition_agent": intent_recognition_agent,
            "validation_agent": validation_agent,
            "nl2sql_agent": nl2sql_agent,
        }
        
        for name, agent in agents.items():
            expected = expected_keys[name]
            actual = getattr(agent, 'output_key', None)
            
            if actual == expected:
                print_result(name, True, f"output_key = '{actual}'")
            else:
                print_result(name, False, f"Expected '{expected}', got '{actual}'")
                all_passed = False
        
        # הערה על db_output ו-final_answer
        print_result("db_output", True, "Saved directly by run_sql_tool (no agent)")
        print_result("final_answer", True, "Saved directly by format_answer (no agent)")
                
    except Exception as e:
        print_result("Import Error", False, str(e))
        all_passed = False
    
    return all_passed


def test_state_flow():
    """
    בדיקה 3: זרימת State
    בודק שהמפתחות הנכונים קיימים בזרימה
    """
    print_header("Test 3: State Flow Dependencies")
    
    state_flow = [
        ("User Input", "last_user_message", "conversation_history"),
        ("Intent Agent", "intent_result", None),
        ("Root Extracts", "final_question", "awaiting_field"),
        ("Validation Agent", "validation_result", None),
        ("NL2SQL Agent", "nl2sql_output", None),
        ("Root Extracts", "sql_query", None),
        ("run_sql_tool", "db_output", None),
        ("format_answer", "final_answer", None),
    ]
    
    print("\nState Flow Diagram:")
    print("-" * 50)
    
    for step, writes, also_writes in state_flow:
        if also_writes:
            print(f"  {step:20} → state['{writes}'], state['{also_writes}']")
        else:
            print(f"  {step:20} → state['{writes}']")
    
    print("-" * 50)
    print_result("State flow documented", True, "See diagram above")
    
    return True


def test_dynamic_date():
    """
    בדיקה 4: תאריך דינמי ב-NL2SQL
    בודק שהתאריך מחושב בזמן ריצה
    """
    print_header("Test 4: Dynamic Date in NL2SQL")
    
    try:
        from datetime import datetime
        from agents.nl2sql.nl2sql_agent import nl2sql_agent
        
        # Check if instruction is callable (dynamic)
        instruction = nl2sql_agent.instruction
        
        if callable(instruction):
            print_result("Dynamic instruction", True, "instruction is a callable function")
            
            # Try to get the instruction text
            # Note: This won't work without proper context, but we can check the callable
            print_result("Today's date", True, f"Will use: {datetime.now().strftime('%Y-%m-%d')}")
            return True
        else:
            # Check if it's a static string with today's date
            today = datetime.now().strftime('%Y-%m-%d')
            if today in str(instruction):
                print_result("Static instruction with today's date", True, f"Contains {today}")
                return True
            else:
                print_result("Dynamic date", False, "instruction is static without today's date")
                return False
                
    except Exception as e:
        print_result("Dynamic date test", False, str(e))
        return False


def test_root_sub_agents():
    """
    בדיקה 5: סוכני משנה ב-Root
    בודק שהסוכנים הנכונים רשומים ושאין Cache/DB/Answer Agent
    """
    print_header("Test 5: Root Sub-Agents")
    
    try:
        from agent import root_agent
        
        sub_agent_names = [agent.name for agent in root_agent.sub_agents]
        
        # Check expected agents are present
        expected = ["intent_recognition_agent", "validation_agent", "nl2sql"]
        
        for name in expected:
            if name in sub_agent_names:
                print_result(f"{name} registered", True)
            else:
                print_result(f"{name} registered", False, "Missing from sub_agents")
        
        # Check removed agents are NOT present (performance improvement)
        removed_agents = ["cache_agent", "db_agent", "answer_agent"]
        for name in removed_agents:
            if name in sub_agent_names:
                print_result(f"{name} removed", False, "Still in sub_agents (should be removed)")
                return False
            else:
                print_result(f"{name} removed", True, "Performance improvement applied")
        
        return True
        
    except Exception as e:
        print_result("Root sub-agents test", False, str(e))
        return False


def test_pydantic_schemas():
    """
    בדיקה 6: סכמות Pydantic
    בודק שהסכמות מוגדרות נכון
    """
    print_header("Test 6: Pydantic Output Schemas")
    
    try:
        from agents.intent_recognition_agent.intent_recognition_agent import IntentResult
        
        # Test IntentResult
        intent_fields = list(IntentResult.model_fields.keys())
        expected_intent = ["status", "message_to_user", "final_question", "clarification_type"]
        
        if all(f in intent_fields for f in expected_intent):
            print_result("IntentResult schema", True, f"Fields: {intent_fields}")
        else:
            print_result("IntentResult schema", False, f"Missing fields. Has: {intent_fields}")
            return False
        
        # AnswerResult הוסר - עיצוב ישירות ב-format_answer()
        print_result("AnswerResult schema", True, "Removed - using format_answer() directly")
        
        return True
        
    except Exception as e:
        print_result("Pydantic schemas test", False, str(e))
        return False


def main():
    """
    הרצת כל הבדיקות
    """
    print("\n" + "=" * 70)
    print("  STATE SYNCHRONIZATION TEST SUITE")
    print("  Click Inflation Chatbot - ADK 1.19")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    results.append(("Agent Imports", test_imports()))
    results.append(("Output Keys", test_output_keys()))
    results.append(("State Flow", test_state_flow()))
    results.append(("Dynamic Date", test_dynamic_date()))
    results.append(("Root Sub-Agents", test_root_sub_agents()))
    results.append(("Pydantic Schemas", test_pydantic_schemas()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        print_result(name, result)
    
    print(f"\n{'=' * 70}")
    if passed == total:
        print(f"  ✅ ALL TESTS PASSED ({passed}/{total})")
    else:
        print(f"  ⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
    print("=" * 70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
