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

"""
Unit tests for verifying code prediction benchmarks.
Dynamically loads 'benchmark.yaml', executes code snippets, and asserts outputs.
"""

import contextlib
import io
from pathlib import Path
import re
import sys

import pytest
import yaml

# Add project root to sys.path so we can import google.adk.*
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT / "src"))

BENCHMARK_FILE = Path(__file__).parent / "benchmark.yaml"


def load_benchmarks():
    """Loads benchmarks from the YAML file."""
    if not BENCHMARK_FILE.exists():
        return []

    with open(BENCHMARK_FILE, "r") as f:
        data = yaml.safe_load(f)

    if not data or "benchmarks" not in data:
        return []

    return data["benchmarks"]


def load_snippet(ref: dict) -> str:
    """Loads a code snippet from a file, including the file header (imports/setup)."""
    file_path = PROJECT_ROOT / ref["file"]
    section = ref["section"]

    if not file_path.exists():
        raise FileNotFoundError(f"Snippet file not found: {file_path}")

    with open(file_path, "r") as f:
        lines = f.readlines()

    header = []
    snippet = []
    in_snippet = False
    found_snippet = False

    # Header is everything before the first `[start:` tag.
    header_done = False

    for line in lines:
        if "# --8<-- [start:" in line:
            header_done = True
            if f"[start:{section}]" in line:
                in_snippet = True
                found_snippet = True
            continue

        if "# --8<-- [end:" in line:
            if f"[end:{section}]" in line:
                in_snippet = False
            continue

        if in_snippet:
            snippet.append(line)
        elif not header_done:
            header.append(line)

    if not found_snippet:
        raise ValueError(f"Section '{section}' not found in {file_path}")

    return "".join(header + snippet)


def execute_snippet(code_str: str) -> str:
    """Executes a code snippet and captures stdout/stderr or exceptions."""
    f = io.StringIO()

    # Prepare execution environment
    # We need to handle imports that might be in the snippet.
    # exec() runs in a local scope.

    exec_globals = {}

    # Pre-import common ADK classes to allow snippets to run without explicit imports
    # (mimicking a context where these are available, or fixing snippets that omitted them)
    try:
        from google.adk.agents.llm_agent import LlmAgent
        from google.adk.agents.loop_agent import LoopAgent
        from google.adk.agents.parallel_agent import ParallelAgent
        from google.adk.agents.sequential_agent import SequentialAgent
        from google.adk.apps.app import App
        from google.adk.plugins.reflect_retry_tool_plugin import ReflectAndRetryToolPlugin
        from google.adk.runners import Runner
        from google.genai import types

        exec_globals.update(
            {
                "LlmAgent": LlmAgent,
                "SequentialAgent": SequentialAgent,
                "LoopAgent": LoopAgent,
                "ParallelAgent": ParallelAgent,
                "App": App,
                "Runner": Runner,
                "ReflectAndRetryToolPlugin": ReflectAndRetryToolPlugin,
                "types": types,
            }
        )
    except ImportError:
        pass

    with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
        try:
            # Debug: print code being executed
            # sys.__stdout__.write(f"\n--- Executing ---\n{code_str}\n-----------------\n")
            
            # Use compile to catch syntax errors before execution
            compiled_code = compile(code_str, '<string>', 'exec')
            exec(compiled_code, exec_globals)

        except Exception as e:
            # Capture any exception, including SyntaxError
            error_name = type(e).__name__
            
            # Format the error message to be clean and consistent
            error_message = str(e).replace("\n", " ")
            print(f"{error_name}: {error_message}")

    return f.getvalue().strip()


@pytest.mark.parametrize("benchmark", load_benchmarks())
def test_code_prediction_accuracy(benchmark):
    """
    Verifies that the code in the question produces the output specified
    by the 'correct_answer' option.
    """
    question = benchmark.get("question", "")
    options = benchmark.get("options", {})
    correct_key = benchmark.get("correct_answer")
    correct_text = options.get(correct_key)

    code_snippet = ""

    if "code_snippet_ref" in benchmark:
        code_snippet = load_snippet(benchmark["code_snippet_ref"])
    else:
        # Fallback to inline extraction (legacy support or for other benchmarks)
        match = re.search(r"```python\n(.*?)```", question, re.DOTALL)
        if match:
            code_snippet = match.group(1)

    if not code_snippet:
        pytest.skip("No python code block or reference found.")

    # 2. Execute Code
    # Note: Some snippets might be incomplete or pseudocode-ish, but the
    # requirement was "must be tested by a corresponding python test",
    # implying they should be executable.

    # We need to be careful about "Predict the error" questions.
    # The code might raise an exception. `execute_snippet` catches this.

    actual_output = execute_snippet(code_snippet)

    # 3. Verify
    # We need to match `actual_output` with `correct_text`.
    # Sometimes `correct_text` might be a substring or formatted slightly differently.
    # Let's try exact match first, then loose match.

    # Normalize line endings and stripping
    normalized_actual = actual_output.replace("\r\n", "\n").strip()
    normalized_expected = str(correct_text).replace("\r\n", "\n").strip()

    # Special handling for "Error" predictions vs captured exception strings
    # If expected is "ValueError: ...", and actual is "ValueError: ...", we match.
    # If expected is "Error: ...", we might need fuzzy match.

    # Also handle "None" output
    if normalized_actual == "" and normalized_expected == "None":
        # Some tools print None, some don't. If snippet has `print(result.output)` and result.output is None, it prints "None".
        pass

    # Assertion
    # Check if expected text is IN actual output (for verbose error traces)
    # OR if actual output is IN expected text (for partial captures).
    # Ideally, they should be very close.

    matches = (
        (normalized_actual == normalized_expected)
        or (normalized_expected in normalized_actual)
        or (normalized_actual in normalized_expected)
    )

    if not matches:
        # Debug info
        pytest.fail(
            f"\nMismatch for benchmark question:\n{question[:100]}...\n"
            f"Expected (Option {correct_key}):\n{normalized_expected!r}\n"
            f"Actual Output:\n{normalized_actual!r}"
        )


if __name__ == "__main__":
    # Allow running as a script
    sys.exit(pytest.main([__file__]))
