# Refactoring Benchmark YAML Files & Diagnosis of Context Regressions

## Objective
1.  Refactor benchmark YAML files to use `code_snippet_ref` correctly (only for questions analyzing code).
2.  Diagnose why adding `llms.txt` context caused performance regressions in certain benchmark suites.

## Part 1: Refactoring Benchmarks

### Actions Taken
1.  **`diagnose_setup_errors_mc`**:
    *   Extracted embedded code blocks into `benchmarks/benchmark_definitions/diagnose_setup_errors_mc/snippets.py`.
    *   Added `pytest.raises` assertions and comments to `snippets.py` to validate that the "buggy" code actually fails as expected.
    *   Updated the YAML file to use `code_snippet_ref` pointing to these validated snippets.
    *   **Result:** 100% pass rate for Ground Truth, confirming validity.

2.  **`configure_adk_features_mc`**:
    *   Initially attempted to refactor this file, but realized `code_snippet_ref` is inappropriate for conceptual questions where code is just illustrative.
    *   **Action:** Reverted the file to its original state (inline code) and deleted the unnecessary snippets file.
    *   **Result:** 100% pass rate for Ground Truth.

## Part 2: Regression Diagnosis

### Issue
Running benchmarks with `llms.txt` context caused a **~7% drop** in `configure_adk_features_mc` and a **~23% drop** in `predict_runtime_behavior_mc` compared to running without context.

### Investigation
A diagnosis script (`diagnose_regressions.py`) was created to compare the model's answers side-by-side.

**Findings:**
1.  **The "None of the above" Trap:** In 27 identified regression cases, the model with context frequently switched its answer from the Correct Option (e.g., 'A', 'B') to **'E' (None of the above)**.
2.  **Context Quality:** Inspection of `llms.txt` revealed it is primarily a high-level overview and a list of links to documentation, rather than containing the detailed API reference or runtime semantics required to answer the specific questions.
3.  **Root Cause:** The model treats the sparse `llms.txt` as a ground-truth knowledge base. When it cannot find specific details (like `EventsCompactionConfig` parameters or `Runner` import paths) within the context, it incorrectly infers that the specific options provided in the question are invalid or unsupported, leading it to choose "None of the above". Without context, the model relies on its general training and intuition, which yields better results for these specific technical questions.

### Conclusion
The `llms.txt` file in its current state is **detrimental** for detailed technical benchmarks because it lacks the necessary depth. To improve performance with context, `llms.txt` must be expanded to include actual API definitions and architectural details, not just links.