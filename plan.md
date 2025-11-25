# Plan: Distinguish Between Crashes and Performance Failures

## Objective

Modify the benchmark suite to differentiate between two types of failures:
1.  **`FAIL_CRASH`**: Hard errors where the generated code is invalid and cannot be executed (e.g., `NameError`, `ImportError`, `SyntaxError`).
2.  **`FAIL_VALIDATION`**: Performance failures where the generated code runs but produces the wrong answer, failing a `pytest` assertion.

This will provide more precise insights into the `GeminiAnswerGenerator`'s failure modes.

## Step-by-step Plan

### 1. Update Data Model

-   **File:** `benchmarks/data_models.py`
-   **Action:**
    -   Create a `BenchmarkResultType(str, Enum)` with three states: `PASS`, `FAIL_VALIDATION`, and `FAIL_CRASH`.
    -   Add a new field, `result_type: BenchmarkResultType`, to the `BenchmarkRunResult` model to store this new, more granular classification.

### 2. Enhance `PytestBenchmarkRunner` to Detect Crashes

-   **File:** `benchmarks/benchmark_runner.py`
-   **Action:**
    -   In the `run_benchmark` method of `PytestBenchmarkRunner`, inspect the `returncode` of the `pytest` subprocess.
    -   If `returncode == 0`, classify the result as `PASS`.
    -   If `returncode == 1`, classify the result as `FAIL_VALIDATION`.
    -   If `returncode > 1` or if specific error patterns (like `NameError`, `ImportError`, `ValidationError`) are found in `stderr`, classify the result as `FAIL_CRASH`.
    -   Update the method's return signature to output the `BenchmarkResultType`.

### 3. Update the Orchestrator to Handle New Result Type

-   **File:** `benchmarks/benchmark_orchestrator.py`
-   **Action:**
    -   In the `_run_single_benchmark` function, update the call to `runner.run_benchmark` to receive the new `BenchmarkResultType`.
    -   In the `except` block for answer generation, explicitly classify the failure as `FAIL_CRASH`.
    -   When constructing the final `BenchmarkRunResult`, correctly populate the new `result_type` field.
    -   Derive the value for the existing `result` field (0 or 1) from the `result_type` to maintain backward compatibility with summary calculations.

### 4. Verify the Implementation

-   **File:** `benchmark_debug.py`
-   **Action:**
    -   Modify the `analyze_logs` function to use the new `result_type` field for filtering. This will allow for separate analysis of crashes and validation failures.
    -   Run the script and verify that the errors previously observed (like `NameError`, `ImportError`) are now correctly categorized as `FAIL_CRASH`, while assertion failures are categorized as `FAIL_VALIDATION`.
