# Click Inflation Chatbot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.x](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![React 18.2](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://react.dev/)

## What is this?

A **production-oriented chatbot** that converts natural language queries into BigQuery SQL.

**Perfect for**: Analytics dashboards, data exploration, automated reporting.

**Key**: Intent Recognition → Validation → NL2SQL → BigQuery

---

## Tech Stack

- **Backend**: FastAPI, Python, Google ADK, BigQuery
- **Frontend**: React, Vite
- **Languages**: Hebrew & English support

---

## Quick Start

### 1️⃣ Backend (Terminal 1)
```bash
cd click_inflation_chatbot
python -m venv .\venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create .env with GOOGLE_API_KEY and GOOGLE_APPLICATION_CREDENTIALS
python -m uvicorn api:app --reload
```
➡️ Backend: http://localhost:8000

### 2️⃣ Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```
➡️ Frontend: http://localhost:5173

### 3️⃣ Test It!
Type in chat: `"How many clicks yesterday?"` or `"כמה clicks אתמול?"`

---

## Key Features

✨ **Dual-Level Caching** — Fast queries, low cost  
🌍 **Bilingual** — Hebrew & English  
🔒 **Read-only SQL** — Safe, no mutations  
💾 **Persistent State** — Session management  
🧩 **Modular Agents** — Easy to extend  

---

## Tests

```bash
python scripts/test_cache_and_counter.py
python scripts/test_state_sync.py
python test_agent_communication.py
```

---

## Project Structure

```
├── agents/              # Intent, Validation, NL2SQL, BigQuery
├── frontend/            # React/Vite UI
├── config/              # Schema & config
├── scripts/             # Tests
├── api.py              # FastAPI app
└── agent.py            # Orchestrator
```

---

## Security

🔐 **Do NOT commit:**
- `.env` files
- API keys, service account JSONs
- Credentials of any kind

Create `.env` locally with:
```
GOOGLE_API_KEY=your_key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json
```

---

## FAQ

**Q: Production-ready?**  
A: Production-oriented. Add auth, rate limiting, monitoring for production.

**Q: Other LLMs?**  
A: Yes, swap Google ADK with OpenAI/Anthropic in agent code.

**Q: Other languages?**  
A: Currently Hebrew & English. Easy to extend.

---

## License

MIT — See [LICENSE](LICENSE)

---

## More Details?

👉 See [DETAILED.md](DETAILED.md) for:
- Deep architecture explanation
- All agent responsibilities
- Environment setup guide
- Troubleshooting
- Roadmap & contributing

---

**Built by Tamar Edel | PractiCode Project** 🚀
