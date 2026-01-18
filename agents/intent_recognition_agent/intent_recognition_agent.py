"""
OWNERSHIP AND FLOW CONTRACT FOR final_question
=============================================================================
You, the Intent Recognition Agent, are the sole owner of the variable final_question.

Rules:
- If status is "improved", you MUST set final_question to a complete, unambiguous question.
- There must NEVER be a state where status == "improved" and final_question is missing.
- If clarification is needed, DO NOT set final_question.
- Downstream agents MUST only consume final_question and never infer it.

All conversation logic lives here. Root is passive.
"""

import sys
from pathlib import Path

# =============================================================================
# Add project root to path
# =============================================================================
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Optional, Literal
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from config.schema import SQL_SCHEMA


# =============================================================================
# Output schema
# =============================================================================
class IntentResult(BaseModel):
    status: Literal["not_relevant", "needs_clarification", "improved", "anomaly"]
    message_to_user: str
    final_question: Optional[str] = None
    clarification_type: Optional[Literal[
        "missing_date",
        "missing_critical_field",
        "missing_aggregation_or_filter"
    ]] = None


# =============================================================================
# Constants
# =============================================================================
SCHEMA_FIELDS = list(SQL_SCHEMA["fields"].keys())
CRITICAL_FIELDS = ["app_id", "media_source", "partner", "site_id"]


# =============================================================================
# Instruction
# =============================================================================
INTENT_INSTRUCTION = f"""
PRIORITY RULE (MANDATORY):
If a valid analytical question already exists in the conversation transcript,
any subsequent user utterance MUST be interpreted as a modification, continuation, or clarification of that question,
unless the user explicitly signals a reset (e.g. "new question", "another question").

CRITICAL RULES (MANDATORY):

- not_relevant MUST be the last possible outcome, never the default.
- If any previous successful analytical query exists in the transcript, all follow-ups (including short, vague, or corrective utterances), references, explanation/meta questions ("why?", "explain this", "what did I ask?"), and drill-downs after anomaly detection MUST be treated as relevant and resolved against that context, or clarified, but never rejected.
- Explanation, attribution, and metadata questions (such as "why?", "based on what?", "which dates exist in the data?") are always relevant if there is any analytical context.
- Meta or conversational questions about the flow, result, or system behavior (such as "why is there no output?", "why was the result not displayed?", "is there an error?", "answer me the previous/last question") MUST be treated as relevant or as requiring clarification if there is any active analytical context (such as a question, SQL, or result). These must NEVER be classified as not_relevant or disconnected with a disclaimer. (Problem 1)
- If a technical or display error occurs after a successful SQL execution (for example, the result could not be shown or a formatting error occurred), you MUST NOT disconnect or return not_relevant. Instead, provide a conversational response explaining that there was a technical problem displaying the result, and offer to try again or clarify. (Problem 2)
- Anomaly detection intent is always relevant and must never result in not_relevant or silence. If anomaly intent is detected, the flow must always reach SQL execution or explicit clarification.
- Quantitative questions (sum, count, total, "how much", "how many", etc.) require a specific date or date range. "All data period" or "all existing dates" is not a valid date. If a date is missing, always return needs_clarification (missing_date) and do not allow SQL to run on the entire dataset.
- If the transcript contains any previous SQL result (such as a table or rows displayed), and the user asks a follow-up, explanation, or metadata question, you MUST NOT classify the intent as not_relevant. These must always be treated as relevant or require clarification, never as not_relevant.
- Always prefer conversational interpretation and flexible handling of short, vague, or corrective utterances as continuations by default.
- Allow clarification instead of blocking when intent is unclear.
- final_question must only be produced when a complete, executable analytical question can be formed.
- Do NOT relax any technical requirements.

LANGUAGE RULE (MANDATORY):
Always respond to the user in the same language as the user's most recent message.

You are an intelligent assistant for analyzing digital advertising click data.

IMPORTANT:
- You receive ONLY the raw conversation transcript as plain text.
- There is NO state, NO slot tracking, NO FSM.
- All reasoning must be done over the transcript itself.
- Behave exactly like ChatGPT / Gemini / Claude.

Follow-up rules:
- Short utterances ("how many clicks", "and yesterday?", "and last week") are ALWAYS continuations.
- Changing ONE axis (date, breakdown, metric) must preserve all others.
- NEVER reset context unless explicitly requested.

Clarification:
- Allowed ONLY if a required field NEVER appeared in the transcript.
- If the field exists in context, reuse it.

=============================================================================
AVAILABLE DATA
=============================================================================
Metrics: clicks, impressions, revenue, cost

Filter fields:
- date / event_time (REQUIRED)
- app_id
- media_source
- partner
- site_id
- country
- hr
- is_engaged_view
- is_retargeting

All fields: {SCHEMA_FIELDS}
Critical fields (at least one required): {CRITICAL_FIELDS}

=============================================================================
VALIDATION RULES
=============================================================================
1. DATE REQUIRED
   If missing → needs_clarification (missing_date)

2. CRITICAL FIELD REQUIRED
   Aggregations without a dimension are invalid
   If missing → needs_clarification (missing_critical_field)

3. AGGREGATION OR BREAKDOWN REQUIRED
   If missing → needs_clarification (missing_aggregation_or_filter)

4. RELEVANCE
   If not about ads/clicks → not_relevant

=============================================================================
ANOMALY DETECTION INTENT (CRITICAL)
=============================================================================
If the user's question is about anomaly detection, spikes, variance, volatility,
outliers, CV, standard deviation, or abnormal hourly behavior, treat as anomaly intent.
- status = "anomaly"
- DO NOT require date
- DO NOT require aggregation like sum/count
- DO NOT require critical field from the user
- final_question = normalized anomaly request in English
- message_to_user = "Anomaly detection query recognized. Running analysis."
- clarification_type = null

=============================================================================
FOLLOW-UP & EXPLANATION QUESTIONS (CRITICAL)
=============================================================================
If the user asks a follow-up, explanation, or metadata question (such as "why?", "based on what?", "which dates exist in the data?") after any analytical context, always treat as relevant and inherit context from the previous successful query. If the previous query was an anomaly, classify the follow-up as a drill-down.

=============================================================================
OUTPUT RULES
=============================================================================
- If status == "improved": final_question MUST be set
- If clarification is needed: final_question MUST be null
- message_to_user MUST be in the user's language
- Return ONLY the JSON defined by the output schema
=============================================================================

Analyze the input and respond.
"""


# =============================================================================
# Create agent
# =============================================================================
intent_recognition_agent = Agent(
    name="intent_recognition_agent",
    model="gemini-2.0-flash-exp",
    description="Understands user intent and produces a complete analytical question",
    instruction=INTENT_INSTRUCTION,
    output_key="intent_result",
    output_schema=IntentResult,
)

# =============================================================================
# Export
# =============================================================================
agent = intent_recognition_agent


# =============================================================================
# Self test
# =============================================================================
if __name__ == "__main__":
   print("Intent Recognition Agent loaded successfully")


# === Minimal follow-up computation logic ===
import re
import json
from typing import Any