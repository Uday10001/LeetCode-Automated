"""
Module 5: Auto-Submission Module
Uses Selenium with a persistent Chrome profile to submit solutions.

IMPORTANT: You must be logged into LeetCode in the Chrome profile before
using auto-submission. Run `python setup_browser.py` to configure.
"""

import os
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Language slugs accepted by LeetCode
LANG_MAP = {
    "python3": "Python3",
    "python": "Python",
    "java": "Java",
    "cpp": "C++",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "go": "Go",
    "rust": "Rust",
}


class LeetCodeSubmitter:
    """
    Automates code submission to LeetCode using Selenium.
    Uses a persistent Chrome profile to maintain login sessions.
    """

    def __init__(self):
        self.profile_dir = os.getenv(
            "CHROME_PROFILE_DIR",
            str(Path.home() / ".leetcode_chrome_profile")
        )

    def _get_driver(self):
        """
        Returns a Selenium Chrome driver with undetected-chromedriver.
        Uses a persistent profile to stay logged in.
        """
        try:
            import undetected_chromedriver as uc
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={self.profile_dir}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # Comment out headless for debugging; keep for production
            # options.add_argument("--headless=new")

            driver = uc.Chrome(options=options)
            driver.implicitly_wait(10)
            return driver
        except ImportError:
            raise ImportError(
                "undetected-chromedriver not installed. "
                "Run: pip install undetected-chromedriver"
            )

    def submit(self, slug: str, code: str, language: str = "python3") -> dict:
        """
        Opens LeetCode problem page, injects code, and submits.
        Returns submission result dict.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        import pyperclip  # pip install pyperclip

        url = f"https://leetcode.com/problems/{slug}/"
        logger.info(f"Opening: {url}")

        driver = self._get_driver()
        result = {"status": "unknown", "runtime": None, "memory": None}

        try:
            driver.get(url)
            wait = WebDriverWait(driver, 20)

            # ── Wait for editor to load ────────────────────────────────────
            time.sleep(3)

            # ── Select correct language ────────────────────────────────────
            try:
                lang_btn = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-cy='lang-select'], .ant-select-selector")
                ))
                lang_btn.click()
                time.sleep(1)

                # Find the language option
                lang_label = LANG_MAP.get(language, "Python3")
                lang_option = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, f"//li[contains(text(), '{lang_label}')]")
                ))
                lang_option.click()
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Language selection failed (may already be correct): {e}")

            # ── Clear editor and inject code ───────────────────────────────
            # LeetCode uses CodeMirror / Monaco editor — use clipboard injection
            editor = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".CodeMirror-code, .view-lines")
            ))

            # Click to focus editor
            editor.click()
            time.sleep(0.5)

            # Select all and replace
            editor.send_keys(Keys.CONTROL + "a")
            time.sleep(0.3)

            # Use pyperclip for reliable paste
            pyperclip.copy(code)
            editor.send_keys(Keys.CONTROL + "v")
            time.sleep(1)

            logger.info("Code injected into editor")

            # ── Click Submit button ────────────────────────────────────────
            submit_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-e2e-locator='console-submit-button'], button[class*='submit']")
            ))
            submit_btn.click()
            logger.info("Submit clicked, waiting for result...")

            # ── Wait for submission result (up to 30s) ─────────────────────
            time.sleep(5)
            for _ in range(10):
                try:
                    status_el = driver.find_element(
                        By.CSS_SELECTOR,
                        "[data-e2e-locator='submission-result'], .result-container"
                    )
                    result["status"] = status_el.text.strip()
                    break
                except Exception:
                    time.sleep(2)

            # Try to extract runtime and memory
            try:
                stats = driver.find_elements(By.CSS_SELECTOR, ".runtime-detail, .memory-detail")
                if len(stats) >= 2:
                    result["runtime"] = stats[0].text.strip()
                    result["memory"] = stats[1].text.strip()
            except Exception:
                pass

            logger.info(f"Submission result: {result}")

        except Exception as e:
            logger.error(f"Submission error: {e}")
            result["status"] = f"Error: {str(e)}"
        finally:
            driver.quit()

        return result
