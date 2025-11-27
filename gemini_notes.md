# Gemini CLI & Benchmark Notes

This document captures key learnings, quirks, and best practices discovered during the development and debugging of the Gemini CLI Answer Generator and the benchmark suite.

## Environment & Execution

### Python Path and Environment
*   **Virtual Environment:** Always use the Python executable within the virtual environment explicitly (e.g., `env/bin/python` or `../env/bin/python`) to ensure dependencies are found. `python` might default to the system python.
*   **Module Discovery:** When running scripts or tests from a subdirectory (like `benchmarks/tests/integration/`), `pytest` might not add the project root to `PYTHONPATH` automatically. Use `PYTHONPATH=. env/bin/pytest ...` or run as a module `env/bin/python -m pytest ...` from the root directory.
*   **Naming Conflicts:** Avoid creating files named `code.py` in the root directory. This conflicts with the Python standard library `code` module, causing `pytest` (specifically `pdb` integration) to crash with `AttributeError: module 'code' has no attribute 'InteractiveConsole'`.

## Asynchronous Execution & Jupyter

### `asyncio.run()` vs `await`
*   **Script Execution:** Standard Python scripts use `asyncio.run(main())` to start the event loop.
*   **Notebook Execution (`papermill` / `ipykernel`):** Jupyter notebooks run inside an **existing** event loop (Tornado). Calling `asyncio.run()` inside a notebook cell raises `RuntimeError: asyncio.run() cannot be called from a running event loop`.
*   **Solution:** When converting a script to a notebook for execution, replace `asyncio.run(main())` with `await main()`. `ipykernel` supports top-level await.

### Papermill Quirks
*   **JSON Output:** `papermill` (via `nbformat`) is very strict about JSON syntax. Generating `.ipynb` files by manually constructing JSON strings is error-prone (escaping newlines, quotes). Always use the `nbformat` library to generate notebooks programmatically.
*   **Kernel Specification:** When running `papermill`, if the input notebook lacks kernel metadata, it fails. Use the `-k` flag (e.g., `-k python3`) to specify the kernel explicitly.

## Gemini CLI Integration

### Deprecated Flags
*   The `--prompt` (or `-p`) flag is deprecated in newer versions of the `gemini` CLI. Pass the prompt as a **positional argument** instead.
    *   **Bad:** `gemini --prompt "Hello" ...`
    *   **Good:** `gemini "Hello" ...`

### Output Parsing
*   **JSON Mode:** The CLI flag `--output-format json` wraps the *entire CLI response* (including stats) in JSON. The model's response is inside the `response` field.
*   **Structured Output Limitation:** The CLI does **not** yet support the native `response_schema` (JSON mode) enforcement available in the SDK. The model returns text (often markdown).
*   **Workaround:** To get structured JSON from the model via CLI, you must use **Prompt Engineering**:
    *   Append explicit instructions: *"IMPORTANT: Output PURE JSON matching this schema..."*
    *   Strip markdown code blocks (```json ... ```) from the output before parsing.

## Benchmark Architecture

### Error Classification
*   Distinguish between **Model Failures** and **Infrastructure Failures**.
*   **Infrastructure:** `ClientError` (429 Resource Exhausted), `SystemExit` (subprocess crash), `TimeoutError`. These indicate the test harness or API limits failed, not necessarily the model's logic.
*   **Model:** `ModelIncorrectAnswer` (MCQ wrong), `ModelAnswerDidNotMatchTemplate` (API understanding wrong format), `AssertionError` (Generated code logic wrong).

### Concurrency
*   **Thundering Herd:** High concurrency (e.g., 50) when running local subprocesses (like `pytest` in `fix_errors` benchmarks) or hitting API rate limits can cause cascading failures (`ResourceExhausted`, system socket limits).
*   **Safe Limits:** A concurrency of `10-20` is generally safe for mixed workloads involving API calls and local subprocess execution.
