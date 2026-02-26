"""
Module 6: Result Analytics & Logging Module
Stores all submissions in a local JSON log file with analytics support.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

LOG_FILE = Path(__file__).parent.parent.parent / "logs" / "submissions.json"


class SubmissionLogger:
    """
    Manages a persistent JSON-based log of all problem submissions.
    Provides analytics methods for reporting.
    """

    def __init__(self, log_path: Path = LOG_FILE):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text(json.dumps([], indent=2))

    def _load(self) -> list:
        try:
            return json.loads(self.log_path.read_text())
        except Exception:
            return []

    def _save(self, data: list):
        self.log_path.write_text(json.dumps(data, indent=2))

    def log(self, entry: dict):
        """Append a new submission entry to the log."""
        data = self._load()
        data.append(entry)
        self._save(data)
        logger.info(f"Logged submission: Problem #{entry.get('problem_number')} — {entry.get('submission_status', 'no-submit')}")

    def get_all(self) -> list:
        """Return all logged submissions, newest first."""
        return list(reversed(self._load()))

    def get_by_problem(self, problem_number: int) -> list:
        """Return all attempts for a specific problem number."""
        return [e for e in self._load() if e.get("problem_number") == problem_number]

    def get_analytics(self) -> dict:
        """
        Returns summary analytics:
        - Total problems attempted
        - Accepted vs failed count
        - Difficulty breakdown
        - Most recent activity
        """
        data = self._load()
        if not data:
            return {"total": 0, "accepted": 0, "failed": 0, "by_difficulty": {}}

        accepted = sum(1 for e in data if "Accepted" in str(e.get("submission_status", "")))
        failed = len(data) - accepted

        difficulty_count = defaultdict(int)
        for e in data:
            diff = e.get("difficulty", "Unknown")
            difficulty_count[diff] += 1

        return {
            "total": len(data),
            "accepted": accepted,
            "failed": failed,
            "acceptance_rate": f"{(accepted / len(data) * 100):.1f}%",
            "by_difficulty": dict(difficulty_count),
            "last_solved": data[-1].get("title") if data else None,
        }
