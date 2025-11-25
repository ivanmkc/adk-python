# Plan: Refactor and Document the `fix_errors` Benchmark

**Overall Goal:** Maintain and improve the `fix_errors` benchmark test suite by ensuring the LLM's view is clean, focused, and well-documented.

**Completed Tasks:**

*   Verified that the initial `fix_errors` benchmark tests function as expected.
*   Removed all instances of intentional code obfuscation (e.g., `base64`, `"".join()`) from the test files for clarity.
*   Identified and addressed multiple issues with the structure of the test cases, where test-running boilerplate was leaking into the LLM's context.

**Current Task:**

1.  **Systematic Refactoring of Test Files:** Go through every test file in `benchmarks/benchmark_definitions/fix_errors/tests/` and meticulously refactor them to adhere to the following strict standards:
    *   The `# LLM_CONTEXT_BEGIN` and `# LLM_CONTEXT_END` markers must **only** enclose the code that is directly relevant to the agent's construction.
    *   All test-running boilerplate—including `pytest` imports, imports from `benchmarks.test_helpers`, `__future__` imports, test functions (`async def test_...`), and helper functions (`run_test`, `assert_test`)—must be moved **outside** of the `LLM_CONTEXT` block.
    *   Any necessary context for the LLM (e.g., Pydantic models, callback functions) will be kept inside the `LLM_CONTEXT` block but outside the `BEGIN: CODE`/`END: CODE` block.

**Next Steps:**

1.  **Update Documentation:** After the refactoring is complete, update the `benchmarks/benchmark_definitions/fix_errors/README.md` file to formally document these new, stricter standards for creating `fix_error` test cases. This will ensure future contributions are consistent.
2.  **Final Verification:** Regenerate the `llm_view.txt` file one last time using the `extract_llm_view.py` script to create a final, clean output for verification.
3.  **Cleanup:** Remove the `extract_llm_view.py` script and `llm_view.txt` file, as they are temporary artifacts for this refactoring task.