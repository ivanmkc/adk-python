# Fix Errors Benchmark

This benchmark evaluates an LLM's ability to fix broken or incomplete ADK agent implementations.

## Structure

Each test case consists of:

1.  A Python test file (`tests/*.py`) containing the broken code.
2.  An entry in `benchmark.yaml` that defines the problem description, requirements, and points to the test file.

## Standards for Creating `fix_error` Test Cases

To ensure consistency and focus the LLM on the relevant task, all `fix_error` test files **must** adhere to the following structure:

1.  **Isolate LLM Context**: The code snippet intended for the LLM to see and modify must be strictly enclosed between `# LLM_CONTEXT_BEGIN` and `# LLM_CONTEXT_END` markers.

2.  **Minimal Context**: The `LLM_CONTEXT` block should be as minimal as possible. It must only contain:
    *   Imports from the ADK (`google.adk.*`) or standard Python libraries (`typing`, `json`, etc.) that are directly used within the LLM's expected solution.
    *   Any necessary data models (e.g., Pydantic `BaseModel` classes) or helper functions (e.g., callback functions) that are *provided* to the LLM as part of the problem's setup and are directly referenced by the agent construction code. These should be defined outside the `# BEGIN: CODE` / `# END: CODE` block but within the `# LLM_CONTEXT_BEGIN` / `# LLM_CONTEXT_END` block.
    *   The `# BEGIN: CODE` and `# END: CODE` markers, which enclose the section of code the LLM needs to write or fix. This block should typically be empty in the test file, as it represents the LLM's output.

3.  **Exclude Test Boilerplate**: All test-running logic and boilerplate must be **outside** the `# LLM_CONTEXT_BEGIN` / `# LLM_CONTEXT_END` block. This includes:
    *   Imports from `__future__`.
    *   Imports from `pytest`.
    *   Imports from `benchmarks.test_helpers`.
    *   `pytestmark` definitions.
    *   Test functions (e.g., `async def test_my_feature(): ...`).
    *   Helper functions for running tests (e.g., `run_test()`, `assert_test()`)

4.  **Explicit Variable Naming**: The `benchmark.yaml` entry for each test case must include a requirement that explicitly states the name of the variable the final solution must be assigned to.
    *   **Example**: `- "The final solution must be assigned to a variable named 
`root_agent`.
    "`

By following these standards, we ensure that the LLM is only presented with the information it needs to solve the agent construction problem, free from the surrounding test infrastructure.
