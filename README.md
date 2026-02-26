# 🤖 LeetCode Automator
### Automated Problem Solving & Submission System
**Course:** Python & Full Stack Development | Lovely Professional University  
**Tech:** FastAPI · GPT-4o · Selenium · HTML/CSS/JS

---

## 🏗 Architecture Overview

```
User (Browser)
    │
    ▼
┌─────────────────────────────────────────┐
│          ONE-PAGE FRONTEND              │
│  index.html (HTML + Tailwind + Vanilla) │
│  • Problem number input                 │
│  • Live pipeline status (WebSocket)     │
│  • Syntax-highlighted solution display  │
│  • Submission history table             │
└──────────────┬──────────────────────────┘
               │ HTTP POST /api/solve
               ▼
┌─────────────────────────────────────────┐
│           FASTAPI BACKEND               │
└──┬───────┬───────┬────────┬─────────────┘
   │       │       │        │
   ▼       ▼       ▼        ▼
Scraper  GPT-4o  Submit  Logger
Module   Module  Module  Module
```

---

## 📁 Project Structure

```
leetcode-automator/
├── backend/
│   ├── main.py                  # FastAPI app, routes, WebSocket
│   └── modules/
│       ├── scraper.py           # Module 1 & 2: LeetCode GraphQL scraper
│       ├── gpt_solver.py        # Module 3: GPT-4o prompt engineering
│       ├── submitter.py         # Module 5: Selenium auto-submitter
│       └── logger.py            # Module 6: JSON analytics & logging
├── frontend/
│   └── index.html               # Single-page app (no framework)
├── logs/
│   └── submissions.json         # Auto-created submission log
├── run.py                       # Server startup script
├── setup_browser.py             # One-time LeetCode login helper
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/leetcode-automator
cd leetcode-automator
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set:
# OPENAI_API_KEY=sk-your-key-here
```

### 3. (Optional) Set Up Browser for Auto-Submit

```bash
python setup_browser.py
# A browser opens → log into LeetCode → close it
# Your session is saved permanently
```

### 4. Run

```bash
python run.py
# Open http://localhost:8000
```

---

## 🔌 API Reference

| Method | Endpoint              | Description               |
|--------|-----------------------|---------------------------|
| `GET`  | `/`                   | Frontend (single-page app)|
| `POST` | `/api/solve`          | Run full pipeline         |
| `GET`  | `/api/logs`           | All submission history    |
| `GET`  | `/api/logs/{num}`     | Logs for one problem      |
| `WS`   | `/ws/status`          | Live pipeline updates     |
| `GET`  | `/api/health`         | Health check              |
| `GET`  | `/docs`               | Swagger API docs          |

### POST /api/solve

**Request:**
```json
{
  "problem_number": 1,
  "auto_submit": false,
  "language": "python3"
}
```

**Response:**
```json
{
  "problem_number": 1,
  "title": "Two Sum",
  "difficulty": "Easy",
  "solution": "class Solution:\n    def twoSum(...):",
  "submission_status": "Accepted",
  "runtime": "52 ms",
  "memory": "16.4 MB",
  "timestamp": "2026-02-26T12:00:00"
}
```

---

## 🧠 Module Details

### Module 1 & 2: LeetCode Scraper (`scraper.py`)
- Uses LeetCode's **official GraphQL API** (no browser needed for fetching)
- Converts problem number → slug → full problem data
- Strips HTML, extracts constraints, gets starter code

### Module 3: GPT Solver (`gpt_solver.py`)
- Model: **GPT-4o** (temperature=0.1 for deterministic output)
- System prompt enforces: optimal complexity, LeetCode class format, inline comments
- Extracts clean code from markdown code blocks

### Module 4: Solution Formatting
- Built into `gpt_solver.py` — code extraction + cleanup
- Frontend syntax highlighting (pure JS, no library)

### Module 5: Auto-Submitter (`submitter.py`)
- Uses **Selenium + undetected-chromedriver** (bypasses bot detection)
- Persistent Chrome profile = no login every time
- Injects code via clipboard, clicks Submit, polls for result

### Module 6: Logger (`logger.py`)
- JSON file-based storage (`logs/submissions.json`)
- Analytics: acceptance rate, difficulty breakdown, history

---

## 🛡 Ethical Use Notice

This tool is built for **learning purposes**:
- You must understand every line of generated code
- Do not use for contest cheating or paid problem bypassing
- LeetCode's Terms of Service apply

---

## 📊 Evaluation Checklist

| Criteria         | Points | Implementation |
|-----------------|--------|----------------|
| Implementation   | 50     | ✅ Full pipeline |
| Code Quality     | 15     | ✅ Modular, documented |
| Blog             | 15     | 📝 Write on Medium |
| Video            | 10     | 🎥 Record with OBS |
| Viva             | 10     | 🎓 Understand each module |

---

## 🎥 OBS Recording Tips

1. Show the frontend → enter problem #1 (Two Sum)
2. Watch the live pipeline stages animate
3. Show the generated solution with syntax highlighting
4. Toggle auto-submit ON → show the Selenium browser opening
5. Show the history table populating
6. Briefly walk through each `modules/` file

---

## 📝 Medium Blog Outline

1. **Problem Statement** — why automate LeetCode?
2. **Architecture** — the 6-module pipeline diagram
3. **LeetCode GraphQL API** — how we fetch without Selenium
4. **Prompt Engineering** — system prompt design decisions
5. **Auto-Submission** — Selenium + persistent Chrome profile trick
6. **Frontend Design** — WebSocket for live updates, syntax highlighting
7. **Results & Learnings**
