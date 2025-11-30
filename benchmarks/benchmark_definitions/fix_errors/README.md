# Fix Errors Benchmark

This benchmark evaluates an LLM's ability to fix broken or incomplete ADK agent implementations.

## Structure

Each test case consists of:

1.  A Python test file (`tests/*.py`) containing the broken code.
2.  An entry in `benchmark.yaml` that defines the problem description, requirements, and points to the test file.

## Standards for Creating `fix_error` Test Cases

To ensure consistency and focus the LLM on the relevant task, all `fix_error` test files **must** adhere to the following:

1.  **Model Output**: The LLM is expected to provide the complete and correct Python solution code as the content of the `unfixed.py` file.

2.  **`create_agent` Function Signature**: The generated Python file **must** contain a function with the exact signature `def create_agent(model_name: str) -> BaseAgent:`.

3.  **Exclude Test Boilerplate**: The solution provided by the LLM should *only* contain the agent definition and necessary imports/helpers. It should **not** include:
    *   Imports from `__future__`.
    *   Imports from `pytest`.
    *   Imports from `benchmarks.test_helpers`.
    *   `pytestmark` definitions.
    *   Test functions (e.g., `async def test_my_feature(): ...`).
    *   Helper functions for running tests (e.g., `run_test()`, `assert_test()`)

4.  **Explicit Variable Naming**: The `benchmark.yaml` entry for each test case must include a requirement that explicitly states the name of the variable the final solution must be assigned to.
    *   **Example**: `- "The final solution must be assigned to a variable named `root_agent`."

By following these standards, we ensure that the LLM is only presented with the information it needs to solve the agent construction problem, free from the surrounding test infrastructure.
