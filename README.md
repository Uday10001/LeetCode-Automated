#  LeetCode Automator
### Automated Problem Solving & Submission System
**Course:** Python & Full Stack Development | Lovely Professional University  
**Tech:** FastAPI · groqAi · Selenium · HTML/CSS/JS

---

##  Quick Start
## Prerequisits
- Python
- groq ai api key
### 1. Clone & Install

```bash
git clone https://github.com/Uday10001/LeetCode-Automated
cd leetcode-automator
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
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

##  API Reference

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

##  Module Details

### Module 1 & 2: LeetCode Scraper (`scraper.py`)
- Uses LeetCode's **official GraphQL API** (no browser needed for fetching)
- Converts problem number → slug → full problem data
- Strips HTML, extracts constraints, gets starter code

### Module 3: GPT Solver (`gpt_solver.py`)
- Model: Groq llama-3.3-70b-versatile
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


