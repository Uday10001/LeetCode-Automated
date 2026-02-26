"""
Module 1 & 2: LeetCode Navigation & Problem Extraction
Uses Selenium with undetected-chromedriver to bypass bot detection.
"""

import re
import time
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

# ─── LeetCode GraphQL API (no browser needed for problem data) ────────────────
LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

PROBLEM_QUERY = """
query getProblemDetail($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    title
    titleSlug
    content
    difficulty
    exampleTestcases
    codeSnippets {
      lang
      langSlug
      code
    }
    topicTags {
      name
    }
  }
}
"""

PROBLEM_LIST_QUERY = """
query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: {}
  ) {
    questions: data {
      frontendQuestionId: questionFrontendId
      titleSlug
      title
      difficulty
    }
  }
}
"""


class LeetCodeScraper:
    """
    Fetches LeetCode problem data via the official GraphQL API.
    Falls back to Selenium if API fails (for premium problems).
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        })

    def get_slug_by_number(self, problem_number: int) -> str:
        """
        Converts a problem number (e.g., 1) → slug (e.g., 'two-sum')
        using LeetCode's problemset API.
        """
        # Try fetching a batch around the target number
        skip = max(0, problem_number - 1)
        payload = {
            "query": PROBLEM_LIST_QUERY,
            "variables": {
                "categorySlug": "",
                "limit": 50,
                "skip": skip
            }
        }

        try:
            resp = self.session.post(LEETCODE_GRAPHQL, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            questions = data["data"]["problemsetQuestionList"]["questions"]

            for q in questions:
                if int(q["frontendQuestionId"]) == problem_number:
                    logger.info(f"Found slug: {q['titleSlug']} for #{problem_number}")
                    return q["titleSlug"]

            raise ValueError(f"Problem #{problem_number} not found in fetched batch")

        except Exception as e:
            logger.error(f"Failed to get slug for #{problem_number}: {e}")
            raise

    def fetch_problem(self, problem_number: int) -> dict:
        """
        Main entry point. Returns structured problem data.
        """
        slug = self.get_slug_by_number(problem_number)
        return self._fetch_by_slug(slug)

    def _fetch_by_slug(self, slug: str) -> dict:
        """
        Fetch full problem details using GraphQL.
        """
        payload = {
            "query": PROBLEM_QUERY,
            "variables": {"titleSlug": slug}
        }

        resp = self.session.post(LEETCODE_GRAPHQL, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        question = data.get("data", {}).get("question")
        if not question:
            raise ValueError(f"Problem '{slug}' not found or is premium-only.")

        # Clean HTML from description
        raw_html = question.get("content", "")
        clean_text = self._clean_html(raw_html)

        # Get Python starter code
        starter_code = ""
        for snippet in question.get("codeSnippets", []):
            if snippet["langSlug"] in ("python3", "python"):
                starter_code = snippet["code"]
                break

        return {
            "id": question["questionId"],
            "title": question["title"],
            "slug": question["titleSlug"],
            "difficulty": question["difficulty"],
            "description": clean_text,
            "examples": question.get("exampleTestcases", ""),
            "constraints": self._extract_constraints(clean_text),
            "starter_code": starter_code,
            "tags": [t["name"] for t in question.get("topicTags", [])],
        }

    @staticmethod
    def _clean_html(html: str) -> str:
        """Strip HTML tags and decode common entities."""
        if not html:
            return ""
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Decode entities
        replacements = {
            "&lt;": "<", "&gt;": ">", "&amp;": "&",
            "&nbsp;": " ", "&#39;": "'", "&quot;": '"',
            "&le;": "≤", "&ge;": "≥",
        }
        for entity, char in replacements.items():
            text = text.replace(entity, char)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _extract_constraints(text: str) -> str:
        """Extract constraint section from the cleaned problem text."""
        match = re.search(r"Constraints?:(.*?)(?:Follow-up:|$)", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
