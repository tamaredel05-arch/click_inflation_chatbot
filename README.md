# Comprehensive Project Summary

## Overview
This project is a full-stack, production-grade chatbot system for click and advertising data analysis. It combines a FastAPI backend (Python) with a modern React frontend (Vite), orchestrated by a modular agent system using Google ADK (Agent Development Kit). The system is designed for natural language understanding, robust validation, automatic SQL generation, and secure database querying (BigQuery).

---

## Technologies & Versions

### Backend
- **Python**: 3.x
- **FastAPI**: (latest, see requirements.txt)
- **Uvicorn**: (ASGI server)
- **Google ADK**: 1.19.0
- **google-generativeai**: 0.8.5
- **google-cloud-bigquery**: (latest)
- **pydantic**: (latest)
- **requests**: >=2.32.4
- **python-dotenv**: >=1.0.0
- **Other**: pandas, db-dtypes, google-auth, starlette, tenacity, typing-extensions, tzlocal, watchdog, websockets

### Frontend
- **React**: ^18.2.0
- **Vite**: ^5.0.10
- **react-dom**: ^18.2.0
- **react-markdown**: ^9.0.1
- **remark-gfm**: ^4.0.0
- **@vitejs/plugin-react**: ^4.2.1

---

## Agent System Architecture

The backend is built around a modular agent pipeline, orchestrated by the Google ADK. Each agent is responsible for a specific stage in the question-to-answer process. The pipeline is:

**User Message → Intent Recognition Agent → Validation Agent → NL2SQL Agent → DB Tool → Answer**

### Agent Roles & Responsibilities

#### 1. Root Orchestrator (agent.py)
- Coordinates the entire conversation flow and state management.
- Receives user messages, maintains session state, and routes requests through the agent pipeline.
- Handles retry logic, clarification attempts, and final user responses.
- Implements persistent state and dual-level caching for performance.

#### 2. Intent Recognition Agent
- Analyzes the user's natural language question.
- Detects missing information (date, critical fields, aggregation).
- Returns a structured JSON with status, improved question, and clarification type if needed.
- Supports both Hebrew and English.

#### 3. Validation Agent
- Receives the improved question from the Intent Agent.
- Checks for technical completeness: date, critical fields, aggregation.
- Approves or rejects questions before SQL conversion.
- Acts as a strict gatekeeper; does not interact directly with the user.

#### 4. NL2SQL Agent
- Converts the validated natural language question into a safe, efficient, read-only SQL query.
- Uses dynamic instructions (e.g., current date) for context-aware SQL generation.
- Returns the SQL in a structured JSON format.

#### 5. DB Tool (BigQuery)
- Executes the generated SQL query on BigQuery.
- Implements dual-level caching: by question and by SQL, for performance and cost savings.
- Returns the query result to the orchestrator for final formatting.

---

## Key Features
- **Dual-Level Caching**: Caches by question and by SQL for efficiency.
- **Persistent State**: Maintains retry counters and session data across HTTP requests.
- **Full Hebrew and English Support**: All agents and logic support both languages.
- **Robust Error Handling**: Structured error responses and logging.
- **Modular, Extensible Design**: Agents can be extended or replaced independently.
- **Automated Tests**: Scripts for cache, state, and business logic validation.

---

## Typical Workflow
1. User submits a question in the chat UI (e.g., "How many clicks were there yesterday?")
2. The backend processes the message through the agent pipeline.
3. The system returns a precise, data-driven answer to the frontend.

---

## Future Extensions
- Support for additional data types and domains.
- Integration with other LLM providers (OpenAI, Anthropic, etc.).
- Enhanced security and permission management.
- Advanced frontend features (visualizations, analytics, etc.).

---
# PractiCode-Project — Click Inflation Agent

This repository contains a small ADK-based agent (root + sub-agents) intended to convert natural language into read-only BigQuery SQL (nl2sql) and other helper agents.

## Architecture

### Active Agents
- **Root Orchestrator** (`agent.py`) - Manages the pipeline and state
- **Intent Recognition Agent** - Analyzes questions, handles Hebrew, detects missing info
- **Validation Agent** - Validates question completeness
- **NL2SQL Agent** - Converts natural language to SQL

### Removed for Performance (Direct Python)
- ~~DB Agent~~ - Replaced by direct `run_sql_tool()` call
- ~~Answer Agent~~ - Replaced by `format_answer()` function
- ~~Cache Agent~~ - Replaced by dual-level caching in `db/tools.py`

### Key Features
- **Dual-Level Caching**: Caches by question (stable) and by SQL (fallback)
- **Persistent State**: Retry counter persists across HTTP requests
- **Hebrew Support**: Full Hebrew language support throughout

## Quickstart (Windows)

1. Create and activate virtualenv (PowerShell):

	```powershell
	python -m venv .\venv
	.\venv\Scripts\Activate.ps1
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	```

2. Create a `.env` or export required environment variables. At minimum the project expects:

	- GOOGLE_API_KEY (if you plan to call generative APIs)
	- GOOGLE_APPLICATION_CREDENTIALS (if using GCP service account)

3. Use the bundled helper to validate the environment and import the agent:

	```powershell
	python run_agent.py
	```

If you get `ModuleNotFoundError: No module named 'google.adk'` it's usually because you didn't activate the project's virtualenv or you didn't install the requirements.

## Quickstart (Unix / macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_agent.py
```

## Running Tests

```powershell
# Test cache and counter functionality
python scripts\test_cache_and_counter.py

# Test state synchronization
python scripts\test_state_sync.py

# Test comprehensive state management
python scripts\test_state_comprehensive.py
```

## Notes

- The repository contains a working pipeline: Intent → Validation → NL2SQL → DB → Answer
- Deprecated agents (`db_agent.py`, `cache_agent.py`, `answer_agent.py`) are stubbed but kept for historical reference
- `run_agent.py` is a friendly wrapper that checks the environment

