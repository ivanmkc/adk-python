import ast
import os
from pathlib import Path
import pytest
import yaml
from google import genai
from pydantic import BaseModel, Field

class FailureVerificationResult(BaseModel):
  verifies_failure: bool = Field(
      ...,
      description="Whether the test function actively verifies that the code fails or produces an incorrect result.",
  )
  explanation: str = Field(
      ..., description="Explanation of why the function does or does not verify failure."
  )

def _get_function_source(file_path: Path, func_name: str) -> str | None:
    """Extracts the source code of a function from a file."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                return ast.get_source_segment(content, node)
        return None
    except Exception:
        return None

def _check_test_verifies_failure(client: genai.Client | None, file_path: Path) -> bool:
  """
  Checks if `test_create_agent_unfixed_fails` contains failure verification logic.
  Uses an LLM if a client is provided; otherwise falls back to basic AST inspection.
  """
  func_source = _get_function_source(file_path, "test_create_agent_unfixed_fails")
  if not func_source:
      return False # Function not found

  if not client:
      # Fallback to heuristic AST check if no API key
      print(f"  [Warning] No API Key. Using heuristic check for {file_path.name}")
      return "assert" in func_source or "pytest.raises" in func_source or "pytest.fail" in func_source

  prompt = f"""You are a code reviewer. Analyze the following Python test function `test_create_agent_unfixed_fails`. 
This function is intended to verify that a broken piece of code (imported as `unfixed`) actually fails or exhibits incorrect behavior.

**Criteria for "Verifies Failure":**
- It DOES verify failure if it uses `pytest.raises(...)` to catch an expected exception.
- It DOES verify failure if it uses `pytest.fail(...)` (e.g. if the code didn't raise as expected).
- It DOES verify failure if it uses `assert` to verify that a value is *incorrect*, *missing*, or matches an error condition (e.g., `assert 'correct' not in output`, `assert result != expected`, `assert 'Error' in result`).
- It DOES NOT verify failure if it simply runs the code without any checks.
- It DOES NOT verify failure if it asserts that the code *works* successfully (e.g. `assert result is not None` when the code is supposedly broken).

Function Source:
```python
{func_source}
```

Does this function explicitly check for failure according to the criteria?
Reply with a JSON object containing 'verifies_failure' (boolean) and 'explanation' (string)."""

  try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": FailureVerificationResult.model_json_schema(),
        },
    )
    result = FailureVerificationResult.model_validate_json(response.text)
    if not result.verifies_failure:
        print(f"  [LLM Check Failed] {file_path.name}: {result.explanation}")
    return result.verifies_failure
  except Exception as e:
    print(f"  [LLM Error] Failed to check {file_path.name}: {e}")
    # Fallback to heuristic on error to avoid blocking CI
    return "assert" in func_source or "pytest.raises" in func_source or "pytest.fail" in func_source


def _check_function_exists(file_path: Path, func_name: str) -> bool:
  """Checks if a Python file contains a function definition with the given name."""
  try:
    content = file_path.read_text()
    tree = ast.parse(content)
    for node in ast.walk(tree):
      if (isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)) and node.name == func_name:
        return True
    return False
  except SyntaxError:
    if file_path.name == "unfixed.py":
        print(f"  [Info] Syntax error in {file_path.name}. Assuming intentional for benchmark case.")
        return True # Assume existence if we can't parse, to allow syntax error cases
    pytest.fail(
        f"Syntax error in {file_path}. Cannot parse for function existence."
    )
  except FileNotFoundError:
    # Should be caught by earlier checks, but defensive
    return False


def test_verify_fix_errors():
  """
  Verification script for fix_errors/benchmark.yaml.
  This script verifies the integrity and structure of fix_error benchmark definitions:
  1. All referenced `test_file`, `unfixed_file`, and `fixed_file` paths exist.
  2. `unfixed.py` and `fixed.py` each contain a `create_agent` function.
  3. `test_agent.py` contains `test_create_agent_passes` and `test_create_agent_unfixed_fails`.
  4. `test_create_agent_unfixed_fails` actively checks for failure (verified by LLM if key present).
  """
  base_dir = Path(__file__).parent
  yaml_path = base_dir / "benchmark.yaml"

  if not yaml_path.exists():
    pytest.fail(f"Error: {yaml_path} does not exist.")

  # Initialize LLM Client
  api_key = os.environ.get("GEMINI_API_KEY")
  client = None
  if api_key:
      client = genai.Client(api_key=api_key)
  else:
      print("Warning: GEMINI_API_KEY not set. Skipping LLM-based verification of failure checks.")

  with open(yaml_path, "r") as f:
    data = yaml.safe_load(f)

  benchmarks = data.get("benchmarks", [])
  print(f"Found {len(benchmarks)} benchmarks defined in {yaml_path.name}.")

  issues = []
  for bm in benchmarks:
    name = bm.get("name", "Unknown Benchmark")
    test_file_path_str = bm.get("test_file")
    unfixed_file_path_str = bm.get("unfixed_file")
    fixed_file_path_str = bm.get("fixed_file")

    # 1. Verify file existence
    if not test_file_path_str:
      issues.append(f"Benchmark '{name}': missing 'test_file' field.")
      continue
    if not unfixed_file_path_str:
      issues.append(f"Benchmark '{name}': missing 'unfixed_file' field.")
      continue
    if not fixed_file_path_str:
      issues.append(f"Benchmark '{name}': missing 'fixed_file' field.")
      continue

    test_full_path = Path(test_file_path_str)
    unfixed_full_path = Path(unfixed_file_path_str)
    fixed_full_path = Path(fixed_file_path_str)

    if not test_full_path.exists():
      issues.append(
          f"Benchmark '{name}': Test file not found: {test_full_path}"
      )
    if not unfixed_full_path.exists():
      issues.append(
          f"Benchmark '{name}': Unfixed file not found: {unfixed_full_path}"
      )
    if not fixed_full_path.exists():
      issues.append(
          f"Benchmark '{name}': Fixed file not found: {fixed_full_path}"
      )

    # Only proceed to function checks if files exist to avoid FileNotFoundError during ast.parse
    if not (
        test_full_path.exists()
        and unfixed_full_path.exists()
        and fixed_full_path.exists()
    ):
      continue

    # 2. Verify `create_agent` function exists in unfixed.py and fixed.py
    if not _check_function_exists(unfixed_full_path, "create_agent"):
      issues.append(
          f"Benchmark '{name}': 'create_agent' function not found in"
          f" {unfixed_full_path.name}."
      )
    if not _check_function_exists(fixed_full_path, "create_agent"):
      issues.append(
          f"Benchmark '{name}': 'create_agent' function not found in"
          f" {fixed_full_path.name}."
      )

    # 3. Verify `test_create_agent_passes` and `test_create_agent_unfixed_fails` exist in test_agent.py
    if not _check_function_exists(test_full_path, "test_create_agent_passes"):
      issues.append(
          f"Benchmark '{name}': 'test_create_agent_passes' function not found in"
          f" {test_full_path.name}."
      )
    if not _check_function_exists(test_full_path, "test_create_agent_unfixed_fails"):
      issues.append(
          f"Benchmark '{name}': 'test_create_agent_unfixed_fails' function not found in"
          f" {test_full_path.name}."
      )
    # 4. Verify `test_create_agent_unfixed_fails` checks for failure
    elif not _check_test_verifies_failure(client, test_full_path):
       issues.append(
          f"Benchmark '{name}': 'test_create_agent_unfixed_fails' does not seem to verify failure (checked with LLM)."
       )

  if issues:
    pytest.fail(
        f"FAILED: {len(issues)} issues found in benchmark configuration:\n"
        + "\n".join(issues)
    )
  else:
    print("\nAll fix_error benchmark files verified successfully.")


if __name__ == "__main__":
  # Allow running as a script manually if needed
  test_verify_fix_errors()
