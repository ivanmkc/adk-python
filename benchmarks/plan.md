# Benchmark Improvement Plan

## Status Overview
**Date:** November 20, 2025
**Verified Benchmarks:**
- `diagnose_setup_errors_mc` (59 questions)
- `predict_runtime_behavior_mc` (59 questions)
- `configure_adk_features_mc` (91 questions)

All suites pass structural verification (`verify_*.py`) and runtime execution (`benchmark_orchestrator.py`).

## Actions Completed
1.  **Standardization:** Enforced `benchmark_type: multiple_choice` across all MC suites to fix Pydantic validation errors.
2.  **Cleanup:** 
    - Removed hundreds of degenerate/repetitive programmatic questions (e.g., 1-100 loop iterations).
    - Consolidated integer-based variations into representative boundary cases (0, 1, 2, 5, 10, 20, 50, 100).
    - Removed invalid name permutation spam.
3.  **Formatting:** Stripped embedded options (e.g., "A. ...") from question text to rely solely on the structured `options` dict.
4.  **Compliance:** Enforced "None of the above" option availability in all questions.
5.  **Bias Correction:** Randomized option order and correct answer keys (A-E) to prevent "Answer A" dominance.
    - Added regression test `benchmarks/tests/unit/test_benchmark_distribution.py` to ensure no single option exceeds 40% frequency.

## Recommendations for Future Improvements

### 1. Semantic Quality & Coverage
-   **Scenario-Based Questions:** Move beyond API signature checks (e.g., "Which import is correct?") to more multi-step reasoning scenarios.
    -   *Example:* Show a buggy agent conversation log and ask to diagnose the root cause (e.g., infinite loop due to missing stop condition vs. model hallucination).
-   **Negative Testing:** Add more questions focusing on error handling and edge cases in user code (e.g., what happens when a tool returns a 500 error string instead of JSON).
-   **New Features:** Add coverage for newer ADK features like:
    -   `CredentialManager` and Auth flows.
    -   `EvalCase` and Evaluation framework details.
    -   Bi-directional streaming configurations.

### 2. Infrastructure
-   **Dynamic Verification:** The `verify_*.py` scripts are static. Implement a dynamic verification step that actually *runs* the code snippet in the question (where applicable) to verify the `correct_answer` matches reality. This prevents the benchmark from drifting from the codebase.
-   **Tagging System:** Add tags to questions (e.g., `tags: ["configuration", "agent-core", "security"]`) to allow running subsets of benchmarks for specific PRs.

### 3. Data Model
-   **Version Pinning:** Add an `adk_version_compatibility` field to questions. Some questions might become obsolete with breaking changes (v1.0 vs v2.0).
-   **Multi-Select:** Support multiple correct answers (Checkbox style) for configuration scenarios where multiple approaches are valid.

## Immediate Next Steps
-   [x] Fix `benchmark_type` schema validation.
-   [x] Verify runtime execution.
-   [x] Fix answer bias (randomize options).
-   [ ] (Optional) Implement dynamic answer verification for `predict_runtime_behavior`.