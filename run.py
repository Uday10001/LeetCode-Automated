#!/usr/bin/env python3
"""
run.py — Start the LeetCode Automator server.
Usage: python run.py
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

def main():
    print("=" * 60)
    print("  🤖 LeetCode Automator")
    print("=" * 60)

    # Check for OpenAI key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n  ⚠  OPENAI_API_KEY not set!")
        print("  Copy .env.example → .env and add your key.\n")
        sys.exit(1)

    print(f"\n  ✓ Starting server at http://{HOST}:{PORT}")
    print(f"  ✓ API docs at http://{HOST}:{PORT}/docs")
    print("  Press CTRL+C to stop\n")

    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        reload_dirs=["backend"]
    )


if __name__ == "__main__":
    main()
