"""
setup_browser.py
Run this ONCE before using auto-submit.
Opens a Chrome window with your persistent profile so you can log into LeetCode manually.
After logging in, close the browser — your session is saved for future automated runs.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROFILE_DIR = os.getenv("CHROME_PROFILE_DIR", str(Path.home() / ".leetcode_chrome_profile"))


def setup():
    print("=" * 60)
    print("  LeetCode Automator — Browser Setup")
    print("=" * 60)
    print(f"\n  Chrome profile will be saved to:\n  {PROFILE_DIR}\n")
    print("  Steps:")
    print("  1. A browser window will open")
    print("  2. Log into your LeetCode account")
    print("  3. Close the browser when done")
    print("  4. Your session is saved — no need to log in again\n")
    input("  Press ENTER to open browser...")

    try:
        import undetected_chromedriver as uc
    except ImportError:
        print("\n  ERROR: undetected-chromedriver not installed.")
        print("  Run: pip install undetected-chromedriver")
        sys.exit(1)

    Path(PROFILE_DIR).mkdir(parents=True, exist_ok=True)

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--start-maximized")

    driver = uc.Chrome(options=options)
    driver.get("https://leetcode.com/accounts/login/")

    print("\n  Browser opened → https://leetcode.com/accounts/login/")
    print("  Log in now, then close the browser window.")

    # Wait until user closes browser
    while True:
        try:
            _ = driver.title
            time.sleep(1)
        except Exception:
            break

    print("\n  ✓ Session saved! You can now use auto-submit.")


if __name__ == "__main__":
    setup()
