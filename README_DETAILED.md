# Click Inflation Chatbot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.x](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![React 18.2](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://react.dev/)

## TL;DR

A **production-oriented** chatbot system that converts natural language queries about click/ad data into BigQuery SQL. Features intent recognition, validation, and caching. Supports Hebrew & English.

---

## Overview

This project combines a **FastAPI** backend (Python) with a modern **React** frontend (Vite), orchestrated by a modular agent system using **Google ADK** (Agent Development Kit). It's designed for:
- 🗣️ Natural language understanding
- ✅ Robust validation
- 🔄 Automatic SQL generation (NL2SQL)
- 🔐 Secure, read-only database querying (BigQuery)
- 🌍 **Bilingual support**: Full Hebrew and English language support

**Perfect for**: Analytics dashboards, data exploration UIs, and automated reporting systems.

---

## Tech Stack

See `requirements.txt` for exact versions.

### Backend
- **Python 3.x** | **FastAPI** | **Uvicorn**
- **Google ADK 1.19.0** | **google-generativeai 0.8.5**
- **BigQuery** | **Pydantic** | **Python-dotenv**

### Frontend
- **React 18.2** | **Vite 5.0** | **React Markdown**

---

## Agent Pipeline Architecture

The backend is built around a **modular agent pipeline** orchestrated by the Google ADK:

```
User Message → Intent Recognition → Validation → NL2SQL → BigQuery → Answer
```

### Agent Roles & Responsibilities

#### 1. Root Orchestrator (`agent.py`)
- Coordinates the entire conversation flow and state management
- Receives user messages, maintains session state, and routes requests through the pipeline
- Handles retry logic, clarification attempts, and final user responses
- Implements persistent state and dual-level caching for performance

#### 2. Intent Recognition Agent
- Analyzes the user's natural language question
- Detects missing information (date, critical fields, aggregation)
- Returns a structured JSON with status, improved question, and clarification type
- Supports both Hebrew and English

#### 3. Validation Agent
- Receives the improved question from the Intent Agent
- Checks for technical completeness: date, critical fields, aggregation
- Approves or rejects questions before SQL conversion
- Acts as a strict gatekeeper; does not interact directly with the user

#### 4. NL2SQL Agent
- Converts the validated natural language question into a safe, efficient, read-only SQL query
- Uses dynamic instructions (e.g., current date) for context-aware SQL generation
- Returns the SQL in a structured JSON format

#### 5. DB Tool (BigQuery)
- Executes the generated SQL query on BigQuery
- Implements dual-level caching: by question and by SQL for performance and cost savings
- Returns the query result to the orchestrator for final formatting

---

## Key Features

- 🎯 **Dual-Level Caching**: Caches by question and by SQL for efficiency
- 💾 **Persistent State**: Maintains retry counters and session data across HTTP requests
- 🌍 **Bilingual Support**: Full Hebrew and English language support throughout
- 🛡️ **Robust Error Handling**: Structured error responses and logging
- 🔧 **Modular Design**: Agents can be extended or replaced independently
- ✅ **Automated Tests**: Scripts for cache, state, and business logic validation
- 🔒 **Read-Only Security**: All BigQuery queries are read-only and safe

---

## Security & Data Privacy

🔐 **Important Security Notes:**

- ✅ **Never commit secrets**: API keys, service account credentials, etc. are in `.gitignore`
- ✅ **Environment variables only**: All sensitive data is loaded from `.env` (not tracked in Git)
- ✅ **Read-only queries**: All BigQuery operations are read-only
- ✅ **Required variables**: `GOOGLE_API_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`

**Setup instructions:**

```bash
# Create .env file (NOT committed to Git)
cp .env.example .env  # if template exists, or create manually

# Add your credentials
GOOGLE_API_KEY=your_key_here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json
```

⚠️ **DO NOT:**
- Push `.env` file to GitHub
- Commit service account keys
- Hardcode credentials in code
- Share API keys in pull requests

---

## Quick Start

### Backend Setup (Windows)

```powershell
# Clone and navigate to project
cd click_inflation_chatbot

# Create virtual environment
python -m venv .\venv
.\venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
# Create a .env file with:
# GOOGLE_API_KEY=your_api_key
# GOOGLE_APPLICATION_CREDENTIALS=path/to/service_account.json

# Run the backend
python -m uvicorn api:app --reload
```

### Backend Setup (macOS/Linux)

```bash
# Clone and navigate to project
cd click_inflation_chatbot

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
export GOOGLE_API_KEY=your_api_key
export GOOGLE_APPLICATION_CREDENTIALS=path/to/service_account.json

# Run the backend
python -m uvicorn api:app --reload
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

The frontend will be available at `http://localhost:5173` by default.

---

## Environment Setup

### Required Variables

```env
# Google Cloud
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json

# Optional
DEBUG=false
```

⚠️ **Security**: Never commit `.env` files. They're already in `.gitignore`.

---

## Testing

```bash
python scripts/test_cache_and_counter.py        # Cache & state tests
python scripts/test_state_sync.py               # State synchronization
python scripts/test_state_comprehensive.py      # Comprehensive state management
```

---

## Project Structure

```
click_inflation_chatbot/
├── agents/
│   ├── intent_recognition_agent/    # Intent detection & missing info
│   ├── validation_agent/            # Question validation
│   ├── nl2sql/                      # Natural language → SQL conversion
│   ├── db/                          # BigQuery tools & caching
│   └── cache_sql/                   # Caching utilities
├── frontend/                         # React/Vite UI
├── config/                           # Schema & configuration
├── scripts/                          # Test utilities
├── agent.py                          # Root orchestrator
└── api.py                            # FastAPI app
```

---

## Security & Data Privacy

✅ **Read-Only Queries** — All BigQuery queries are read-only and safe
✅ **No Key Exposure** — API keys stored in `.env` (never committed)
✅ **Input Validation** — All user input validated before SQL generation
✅ **Error Safety** — No sensitive data leaked in error messages

---

## How to Run (End-to-End)

### 1️⃣ Backend

```bash
# Terminal 1: Navigate to project root
cd click_inflation_chatbot

# Create & activate virtual environment
python -m venv .\venv
.\venv\Scripts\Activate.ps1  # Windows
# OR
source .venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file with credentials (see Security section above)
# GOOGLE_API_KEY=...
# GOOGLE_APPLICATION_CREDENTIALS=...

# Start backend server
python -m uvicorn api:app --reload

# ✅ Backend running at: http://localhost:8000
# 📚 API docs at: http://localhost:8000/docs
```

### 2️⃣ Frontend

```bash
# Terminal 2: Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# ✅ Frontend running at: http://localhost:5173
# Open in browser: http://localhost:5173
```

### 3️⃣ Test It!

**In the chat UI (at http://localhost:5173):**
- Type: "How many clicks were there yesterday?"
- Or in Hebrew: "כמה clicks היו אתמול?"
- The system will go through Intent → Validation → NL2SQL → BigQuery → Answer pipeline

---

## Demo / Screenshots

> 💡 **Coming soon**: Add screenshots or GIF of the chatbot interface here
> 
> For now, the chatbot processes queries like:
> - "כמה clicks בחודש האחרון?" (Hebrew)
> - "Show me top 10 campaigns" (English)
> - "Total revenue yesterday" (English)

---

## API Example

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many clicks yesterday?", "session_id": "user123"}'
```

Response:
```json
{
  "response": "There were X clicks yesterday.",
  "status": "success",
  "session_id": "user123"
}
```

---

## Project Structure

```
click_inflation_chatbot/
├── agents/                          # AI agent pipeline
│   ├── intent_recognition_agent/   # Intent detection & missing info
│   ├── validation_agent/           # Question validation
│   ├── nl2sql/                     # NL → SQL conversion
│   ├── cache_sql/                  # Caching layer
│   └── db/                         # BigQuery integration
├── frontend/                        # React/Vite UI
│   └── src/
│       ├── components/             # React components
│       ├── App.jsx                 # Main app
│       └── styles.css
├── config/                          # Config & schema
├── scripts/                         # Test scripts
├── agent.py                         # Root orchestrator
├── api.py                           # FastAPI app
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## Running Tests

```bash
# Test cache & counter
python scripts/test_cache_and_counter.py

# Test state sync
python scripts/test_state_sync.py

# Test comprehensive state
python scripts/test_state_comprehensive.py

# Test agent communication
python test_agent_communication.py

# Test API
python test_api.py
```

---

## Roadmap

- [ ] Support for OpenAI, Anthropic LLMs
- [ ] GraphQL API layer
- [ ] Advanced data visualizations
- [ ] Multi-dataset support
- [ ] Role-based access control (RBAC)
- [ ] Docker & Cloud Run deployment
- [ ] Rate limiting & authentication
- [ ] Monitoring & logging dashboard

---

## FAQ

**Q: Can I use this with a different LLM?**  
A: Yes! The agent framework is modular. Replace the intent/NL2SQL agents to use OpenAI/Anthropic instead of Google ADK.

**Q: Is this production-ready?**  
A: It's production-oriented and designed for analytics use. For production, add auth, rate limiting, monitoring, and audit logs.

**Q: Does it support other languages?**  
A: Currently supports Hebrew & English. Easy to extend to other languages by updating agent prompts.

**Q: How much does BigQuery cost?**  
A: Depends on data scanned. The caching layer helps reduce costs significantly.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Contact & Contributing

- **Author**: Tamar Edel
- **Project**: PractiCode - Click Inflation Chatbot
- **Questions?** Open an issue on GitHub or contact the maintainers

**Want to contribute?** We welcome PRs, bug reports, and feature requests!

---

**Happy coding! 🚀**