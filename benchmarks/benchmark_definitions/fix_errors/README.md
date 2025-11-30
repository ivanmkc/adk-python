# Fix Errors Benchmark

This benchmark evaluates an LLM's ability to fix broken or incomplete ADK agent implementations.

## Structure

The benchmark uses a directory-based structure for test cases. All cases are located in the `cases/` directory.

Each test case consists of a dedicated subdirectory (e.g., `cases/01_my_case/`) containing three essential files:

1.  **`unfixed.py`**: A Python file containing the broken or incomplete code. This is what the LLM reads and is asked to fix.
2.  **`fixed.py`**: A Python file containing the correct, working implementation. This serves as the ground truth.
3.  **`test_agent.py`**: A standard `pytest` file that imports the generated solution (or the fixed/unfixed code during testing) and runs assertions to verify its correctness.

An entry in `benchmark.yaml` points to this directory and defines the problem description and requirements.

## Standards for Creating `fix_error` Test Cases

To ensure consistency and focus the LLM on the relevant task, all `fix_error` test cases **must** adhere to the following:

1.  **Model Output**: The LLM is expected to provide the complete and correct Python solution code. This code typically replaces the content of `unfixed.py`.

2.  **`create_agent` Function Signature**: The generated Python file (and thus `fixed.py` and `unfixed.py`) **must** contain a function with the exact signature `def create_agent(model_name: str) -> BaseAgent:`. The `test_agent.py` will import and call this function.

3.  **Exclude Test Boilerplate**: The solution provided by the LLM should *only* contain the agent definition and necessary imports/helpers. It should **not** include:
    *   Imports from `__future__`.
    *   Imports from `pytest`.
    *   Imports from `benchmarks.test_helpers`.
    *   `pytestmark` definitions.
    *   Test functions (e.g., `async def test_my_feature(): ...`).
    *   Helper functions for running tests (e.g., `run_test()`, `assert_test()`)

4.  **Explicit Variable Naming**: The `benchmark.yaml` entry for each test case must include a requirement that explicitly states the name of the variable the final solution must be assigned to, if applicable (though `create_agent` is the primary interface).

By following these standards, we ensure that the LLM is only presented with the information it needs to solve the agent construction problem, free from the surrounding test infrastructure.
