"""
Module 3: Prompt Engineering & GPT Integration
Generates optimized LeetCode solutions using OpenAI GPT-4o.
"""

import os
import re
import logging
from openai import AsyncOpenAI
from groq import AsyncGroq
logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an expert competitive programmer and LeetCode specialist.
Your task is to solve LeetCode problems with OPTIMAL time and space complexity.

Rules:
1. Always use the exact class/function signature provided.
2. Provide ONLY the Python code inside a ```python code block — nothing else outside it.
3. Add clear inline comments explaining the algorithm and key steps.
4. Use the most efficient algorithm (prefer O(n) over O(n²) where possible).
5. Handle all edge cases mentioned in the constraints.
6. After the solution, add a commented block:
   # Time Complexity: O(...)
   # Space Complexity: O(...)
   # Algorithm: (one line explanation)
"""

USER_PROMPT_TEMPLATE = """Solve this LeetCode problem:

**Problem #{number}: {title}**

{description}

**Example Test Cases:**
{examples}

**Constraints:**
{constraints}

**Starter Code (use this exact signature):**
```python
{starter_code}
```

Provide only the complete Python solution in a ```python code block."""


class GPTSolver:
    """
    Uses OpenAI GPT-4o to generate optimized Python solutions
    for LeetCode problems with structured prompt engineering.
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY not set. "
                "Add it to your .env file: API_KEY=sk-..."
            )
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
    async def generate_solution(
        self,
        problem_number: int,
        title: str,
        description: str,
        examples: str,
        constraints: str,
        starter_code: str = "",
        language: str = "python3",
    ) -> str:
        """
        Sends the problem to GPT-4o and returns clean, runnable Python code.
        """
        if not starter_code:
            starter_code = "class Solution:\n    def solve(self, ...):\n        pass"

        user_message = USER_PROMPT_TEMPLATE.format(
            number=problem_number,
            title=title,
            description=description,
            examples=examples or "See problem statement",
            constraints=constraints or "See problem statement",
            starter_code=starter_code,
        )

        logger.info(f"Sending Problem #{problem_number} to GPT-4o...")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,  # Low temperature = more deterministic, accurate code
            max_tokens=2048,
        )

        raw_response = response.choices[0].message.content
        logger.info(f"GPT-4o responded with {len(raw_response)} characters")

        return self._extract_code(raw_response)

    @staticmethod
    def _extract_code(gpt_output: str) -> str:
        """
        Extracts code from GPT markdown code blocks.
        Handles ```python ... ``` and ``` ... ``` patterns.
        """
        # Try to extract from ```python block
        match = re.search(r"```python\s*(.*?)```", gpt_output, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Fallback: generic code block
        match = re.search(r"```\s*(.*?)```", gpt_output, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Last resort: return raw (might already be clean code)
        return gpt_output.strip()
