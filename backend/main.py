"""
LeetCode Automator - FastAPI Backend
Course: Python & Full Stack Development | LPU
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from backend.modules.scraper import LeetCodeScraper
from backend.modules.gpt_solver import GPTSolver
from backend.modules.submitter import LeetCodeSubmitter
from backend.modules.logger import SubmissionLogger

# ─── App Setup ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="LeetCode Automator API",
    description="Automated LeetCode problem solving and submission using GPT",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

logger = logging.getLogger(__name__)
submission_logger = SubmissionLogger()

# ─── Models ───────────────────────────────────────────────────────────────────

class SolveRequest(BaseModel):
    problem_number: int
    auto_submit: bool = False
    language: str = "python3"

class SolveResponse(BaseModel):
    problem_number: int
    title: str
    difficulty: str
    solution: str
    submission_status: str | None = None
    runtime: str | None = None
    memory: str | None = None
    timestamp: str

# ─── WebSocket for live status updates ────────────────────────────────────────

active_connections: list[WebSocket] = []

async def broadcast(message: dict):
    for ws in active_connections:
        try:
            await ws.send_json(message)
        except Exception:
            pass

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = frontend_path / "index.html"
    return HTMLResponse(content=index_path.read_text())

@app.post("/api/solve", response_model=SolveResponse)
async def solve_problem(req: SolveRequest):
    """
    Full pipeline:
    1. Fetch problem from LeetCode
    2. Send to GPT for solution
    3. (Optional) Auto-submit
    4. Log result
    """
    await broadcast({"stage": "starting", "message": f"🔍 Looking up Problem #{req.problem_number}..."})

    # ── Stage 1: Scrape ────────────────────────────────────────────────────
    scraper = LeetCodeScraper()
    try:
        await broadcast({"stage": "scraping", "message": "📄 Extracting problem statement..."})
        problem_data = await asyncio.to_thread(scraper.fetch_problem, req.problem_number)
    except Exception as e:
        await broadcast({"stage": "error", "message": f"❌ Scraping failed: {str(e)}"})
        raise HTTPException(status_code=404, detail=f"Could not fetch problem #{req.problem_number}: {str(e)}")

    # ── Stage 2: GPT Solution ──────────────────────────────────────────────
    await broadcast({"stage": "solving", "message": "🤖 GPT is generating an optimized solution..."})
    solver = GPTSolver()
    try:
        solution_code = await solver.generate_solution(
            problem_number=req.problem_number,
            title=problem_data["title"],
            description=problem_data["description"],
            examples=problem_data.get("examples", ""),
            constraints=problem_data.get("constraints", ""),
            language=req.language
        )
    except Exception as e:
        await broadcast({"stage": "error", "message": f"❌ GPT error: {str(e)}"})
        raise HTTPException(status_code=500, detail=f"GPT API error: {str(e)}")

    # ── Stage 3: Auto-Submit ───────────────────────────────────────────────
    submission_status = None
    runtime = None
    memory = None

    if req.auto_submit:
        await broadcast({"stage": "submitting", "message": "🚀 Submitting solution to LeetCode..."})
        submitter = LeetCodeSubmitter()
        try:
            result = await asyncio.to_thread(
                submitter.submit,
                slug=problem_data["slug"],
                code=solution_code,
                language=req.language
            )
            submission_status = result.get("status", "Unknown")
            runtime = result.get("runtime")
            memory = result.get("memory")
            await broadcast({
                "stage": "submitted",
                "message": f"✅ Submission result: {submission_status}"
            })
        except Exception as e:
            submission_status = f"Submission failed: {str(e)}"
            await broadcast({"stage": "warning", "message": f"⚠️ {submission_status}"})

    # ── Stage 4: Log ───────────────────────────────────────────────────────
    timestamp = datetime.now().isoformat()
    submission_logger.log({
        "problem_number": req.problem_number,
        "title": problem_data["title"],
        "difficulty": problem_data["difficulty"],
        "solution": solution_code,
        "submission_status": submission_status,
        "runtime": runtime,
        "memory": memory,
        "timestamp": timestamp
    })

    await broadcast({"stage": "done", "message": "🎉 All done!"})

    return SolveResponse(
        problem_number=req.problem_number,
        title=problem_data["title"],
        difficulty=problem_data["difficulty"],
        solution=solution_code,
        submission_status=submission_status,
        runtime=runtime,
        memory=memory,
        timestamp=timestamp
    )

@app.get("/api/logs")
async def get_logs():
    """Retrieve all past submissions."""
    return submission_logger.get_all()

@app.get("/api/logs/{problem_number}")
async def get_log_by_problem(problem_number: int):
    """Retrieve logs for a specific problem number."""
    logs = submission_logger.get_by_problem(problem_number)
    if not logs:
        raise HTTPException(status_code=404, detail="No logs found for this problem.")
    return logs

@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
