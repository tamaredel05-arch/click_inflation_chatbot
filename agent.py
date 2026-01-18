"""
Full Orchestrator — ADK 1.19
Workflow:
Intent → Validation → NL2SQL → DB → Answer
"""

import sys
from pathlib import Path
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.genai.types import Content, Part

# =============================================================================
# Add project root to path
# =============================================================================
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# =============================================================================
# Import agents and tools
# =============================================================================
from agents.intent_recognition_agent.intent_recognition_agent import (
    intent_recognition_agent
)
from agents.validation_agent.validation_agent import validation_agent
from agents.nl2sql.nl2sql_agent import nl2sql_agent
from agents.db.tools import run_sql_tool, RunSQLInput


# =============================================================================
# Answer formatter (replaces Answer Agent)
# =============================================================================
def format_answer(db_output: dict) -> str:
    if not db_output:
        return "No results found."

    rows = db_output.get("rows", [])
    from_cache = db_output.get("from_cache", False)

    if not rows:
        return "No results found."

    source_note = "  (from cache)" if from_cache else "  (from database)"

    # Single scalar result
    if len(rows) == 1 and len(rows[0]) == 1:
        value = list(rows[0].values())[0]
        if value is None:
            return f"**Result**: No data found{source_note}"
        return f"**Result**: {value:,}{source_note}"

    # Table result
    headers = list(rows[0].keys())
    lines = [
        f"**Query returned {len(rows)} rows**{source_note}",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for row in rows[:20]:
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")

    if len(rows) > 20:
        lines.append(f"\n*Showing 20 of {len(rows)} rows*")

    return "\n".join(lines)


# =============================================================================
# ORCHESTRATOR
# =============================================================================
class ClickInflationOrchestrator(BaseAgent):

    def __init__(self):
        super().__init__(
            name="click_inflation_orchestrator",
            sub_agents=[
                intent_recognition_agent,
                validation_agent,
                nl2sql_agent,
            ],
        )

    async def _run_async_impl(self, context) -> AsyncGenerator[Event, None]:
        state = context.session.state

        # ---------------------------------------------------------------------
        # 1. Maintain ONLY plain-text transcript (no semantic state)
        # ---------------------------------------------------------------------
        state.setdefault("conversation_text", [])

        user_text = ""
        if context.user_content and context.user_content.parts:
            user_text = context.user_content.parts[0].text.strip()

        if user_text:
            state["conversation_text"].append(f"User: {user_text}")

        full_conversation = "\n".join(state["conversation_text"])

        # Send full transcript to Intent Agent
        context.user_content = Content(
            role="user",
            parts=[Part(text=full_conversation)]
        )

        # ---------------------------------------------------------------------
        # 2. Intent Recognition
        # ---------------------------------------------------------------------
        async for ev in intent_recognition_agent.run_async(context):
            yield ev

        intent_result = state.get("intent_result", {})
        status = intent_result.get("status")
        message = intent_result.get("message_to_user")
        final_question = intent_result.get("final_question")

        # Make final_question available downstream
        state["final_question"] = final_question
        state["status"] = status

        # ---------------------------------------------------------------------
        # 3. Stop early if clarification or not relevant
        # ---------------------------------------------------------------------
        if status in ("needs_clarification", "not_relevant"):
            if message:
                yield Event(
                    author=self.name,
                    content=Content(
                        role="model",
                        parts=[Part(text=message)]
                    )
                )
            return

        # ---------------------------------------------------------------------
        # 4. Validation (technical gate only)
        # ---------------------------------------------------------------------
        async for ev in validation_agent.run_async(context):
            yield ev

        validation_result = state.get("validation_result", {})
        if validation_result.get("status") != "approved":
            return

        # ---------------------------------------------------------------------
        # 5. NL2SQL
        # ---------------------------------------------------------------------
        async for ev in nl2sql_agent.run_async(context):
            yield ev

        nl2sql_output = state.get("nl2sql_output", {})
        sql = nl2sql_output.get("sql_query")
        output_tables = nl2sql_output.get("output_tables")

        # ---------------------------------------------------------------------
        # ❌ No valid SQL
        # ---------------------------------------------------------------------
        if not sql or sql == "FALLBACK_NO_EXECUTION":
            yield Event(
                author=self.name,
                content=Content(
                    role="model",
                    parts=[Part(
                        text="Unable to generate a valid SQL query for your request."
                    )]
                )
            )
            return

        # ---------------------------------------------------------------------
        #  ANOMALY MODE
        # ---------------------------------------------------------------------
        if output_tables:
            try:
                db_result = run_sql_tool(
                    RunSQLInput(
                        sql=sql,
                        final_question=final_question,
                        output_tables=output_tables
                    )
                )
            except Exception as e:
                yield Event(
                    author=self.name,
                    content=Content(
                        role="model",
                        parts=[Part(
                            text=f"Anomaly SQL execution failed: {str(e)}"
                        )]
                    )
                )
                return

            state["output_tables"] = output_tables

            # Get list of created tables (from SQL execution result)
            anomaly_info = db_result.get("output_tables", [])
            tables_list = "\n".join(
                f"- {table_name}"
                for table_name in anomaly_info
            )

            # First, yield the success message with table names
            yield Event(
                author=self.name,
                content=Content(
                    role="model",
                    parts=[Part(
                        text=(
                            " **Anomaly detection completed successfully.**\n\n"
                            "**Created tables:**\n"
                            f"{tables_list}\n\n"
                            "**Fetching table results...**"
                        )
                    )]
                )
            )

            # Fetch and display data from each created table
            for table_name in anomaly_info:
                try:
                    # Query each table to get sample data
                    query = f"SELECT * FROM `{table_name}` LIMIT 20"
                    table_result = run_sql_tool(
                        RunSQLInput(
                            sql=query,
                            final_question=None  # No caching for table preview queries
                        )
                    )
                    
                    # Format the results
                    formatted_result = format_answer(table_result)
                    
                    # Yield the table data
                    yield Event(
                        author=self.name,
                        content=Content(
                            role="model",
                            parts=[Part(
                                text=(
                                    f"### 📊 Table: `{table_name}`\n\n"
                                    f"{formatted_result}\n"
                                )
                            )]
                        )
                    )
                except Exception as e:
                    # If there's an error fetching table data, just show the table name
                    yield Event(
                        author=self.name,
                        content=Content(
                            role="model",
                            parts=[Part(
                                text=(
                                    f"### Table: `{table_name}`\n\n"
                                    f" Could not fetch table data: {str(e)}\n"
                                )
                            )]
                        )
                    )
            
            return

        # ---------------------------------------------------------------------
        # NORMAL MODE
        # ---------------------------------------------------------------------
        db_result = run_sql_tool(
            RunSQLInput(
                sql=sql,
                final_question=final_question
            )
        )

        answer = format_answer(db_result)

        yield Event(
            author=self.name,
            content=Content(
                role="model",
                parts=[Part(text=answer)]
            )
        )


# =============================================================================
# EXPORT
# =============================================================================
root_agent = ClickInflationOrchestrator()
agent = root_agent
