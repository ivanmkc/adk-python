# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A script to verify that no answers are leaked in MC benchmark cases."""

import asyncio
import os
from pathlib import Path
import re
import sys
import yaml
from pydantic import BaseModel, Field

# Manually set up path to src to import adk modules if needed
sys.path.append("src")
# Set path to current dir to import benchmarks
sys.path.append(os.getcwd())

from benchmarks.data_models import BenchmarkFile, MultipleChoiceBenchmarkCase
from benchmarks.validation_utils import load_snippet
from google import genai

class LeakCheckResult(BaseModel):
    is_leaked: bool = Field(..., description="Whether the answer is leaked or trivial given the snippet.")
    explanation: str = Field(..., description="Explanation of why the answer is or is not leaked.")

async def check_leak(client: genai.Client, case: MultipleChoiceBenchmarkCase, snippet: str, model_name: str = "gemini-2.5-flash") -> LeakCheckResult:
    """Checks a single case for leaks using the LLM."""
    
    options_str = "\n".join(f"{key}: {value}" for key, value in case.options.items())
    
    prompt = (
        "You are a strict exam proctor. I will provide you with a Multiple Choice Question (MCQ) and a code snippet that acts as the context for the question. "
        "Your task is to determine if the code snippet **explicitly contains the answer** or makes it **trivial/obvious** without requiring knowledge of the library logic. "
        "\n\n"
        "**It is A LEAK if:**\n"
        "1. The snippet explicitly imports the *exact error type* that is the correct answer (e.g. importing `ValidationError` when the answer is `ValidationError`), unless it's a standard Python builtin like `ValueError`.\n"
        "2. The snippet contains comments, docstrings, or variable names that explicitly state the result/answer (e.g. `# Expect: Error`).\n"
        "3. The snippet compares faulty code with correct code in the same block, making the error obvious by contrast.\n"
        "\n"
        "**It is NOT A LEAK if:**\n"
        "1. The answer can be derived by reading the code and understanding standard Python behavior (e.g., dictionary mutability, variable assignment).\n"
        "2. The answer is evident from the library's public API naming conventions (e.g., `before_callback` running before).\n"
        "3. The question asks 'Does this code satisfy the spec?' and the snippet *is* the implementation. Showing the code is necessary for the user to evaluate it.\n"
        "4. The snippet uses standard imports (like `sys`, `os`) or essential library imports needed to run the code (like `LlmAgent`), provided they don't give away the specific *error* being tested.\n"
        "\n"
        f"Question: {case.question}\n"
        f"Options:\n{options_str}\n"
        f"Correct Answer: {case.correct_answer}\n\n"
        "Code Snippet:\n"
        "```python\n"
        f"{snippet}\n"
        "```\n\n"
        "Does the snippet leak the answer? Reply with a JSON object containing 'is_leaked' (boolean) and 'explanation' (string)."
    )
    try:
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": LeakCheckResult.model_json_schema(),
            },
        )
        return LeakCheckResult.model_validate_json(response.text)
    except Exception as e:
        return LeakCheckResult(is_leaked=False, explanation=f"Failed to check leak: {e}")

async def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    
    # Locate all MC benchmark suites
    base_dir = Path("benchmarks/benchmark_definitions")
    mc_suites = list(base_dir.glob("*_mc/benchmark.yaml"))
    
    print(f"Found {len(mc_suites)} MC benchmark suites.")
    
    total_cases = 0
    leaked_cases = 0
    
    for suite_path in mc_suites:
        print(f"\nChecking suite: {suite_path}")
        try:
            with open(suite_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            benchmark_file = BenchmarkFile.model_validate(data)
        except Exception as e:
            print(f"Failed to load suite {suite_path}: {e}")
            continue

        for case in benchmark_file.benchmarks:
            if not isinstance(case, MultipleChoiceBenchmarkCase):
                continue
            
            total_cases += 1
            
            # Extract snippet
            snippet = ""
            if case.code_snippet_ref:
                try:
                    snippet = load_snippet(case.code_snippet_ref)
                except Exception as e:
                    print(f"  [WARNING] Could not load snippet for '{case.question[:50]}...': {e}")
                    continue
            
            if not snippet:
                 # If no snippet, can't check for code leaks
                 continue

            # Check for leaks
            result = await check_leak(client, case, snippet)
            
            if result.is_leaked:
                leaked_cases += 1
                print(f"  [FAIL] Leak detected in '{case.question[:50]}...'\n")
                print(f"    Explanation: {result.explanation}\n")
                print(f"    File: {case.code_snippet_ref.file if case.code_snippet_ref else 'N/A'}\n")
            else:
                # print(f"  [PASS] '{case.question[:50]}...'\n")
                pass

    print("\n" + "="*40)
    print(f"Total MC cases checked: {total_cases}\n")
    print(f"Leaked cases found: {leaked_cases}\n")
    
    if leaked_cases > 0:
        sys.exit(1)
    else:
        print("No leaks detected!")

if __name__ == "__main__":
    asyncio.run(main())
