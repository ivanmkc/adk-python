# ADK Benchmark Framework

This directory contains a data-driven framework for evaluating and comparing different code generation strategies, referred to as "Answer Generators."

## Overview

The benchmark framework is orchestrated by `benchmark_orchestrator.py` and initiated by `test_benchmarks.py`. It operates by running `AnswerGenerator` classes against benchmark cases defined in YAML files. The results are compiled into a pandas DataFrame that scores the performance of each generator.

### Architecture Call Graph

```
   +-----------------------+
   |  test_benchmarks.py   |  (pytest entry point)
   +-----------------------+
              |
              | Calls
              v
   +---------------------------+
   | benchmark_orchestrator.py |  (Main orchestrator)
   +---------------------------+
      |           |           |
      | Uses      | Uses      | Uses
      v           v           v
+---------------+  +----------------------+  +---------------------+
| data_models.py|  | answer_generators.py |  | benchmark_runner.py |
+---------------+  +----------------------+  +---------------------+
                      |
                      | Reads from
                      v
        +---------------------------+
        | test_data/ground_truth/   |
        +---------------------------+

```

### Key Components

*   **`test_benchmarks.py`**: The main `pytest` entry point for validating the framework's integrity.
*   **`benchmark_orchestrator.py`**: The central orchestrator that iterates through benchmarks, calls the appropriate runner for each case, and aggregates results.
*   **`benchmark_runner.py`**: Defines strategies for executing benchmarks (e.g., `PytestBenchmarkRunner`).
*   **`answer_generators.py`**: Defines different code generation strategies (e.g., `GroundTruthAnswerGenerator`).
*   **`data_models.py`**: Pydantic models for the benchmark YAML files.
*   **`benchmark_definitions/`**: Contains the YAML data files and test templates.
*   **`test_data/ground_truth/`**: Contains the correct code snippets for `fix_error` benchmarks.

## Usage Philosophy

There are two distinct ways to use this framework: validating its integrity and evaluating candidate answer generators.

### 1. Validating the Benchmark Framework

Before running experiments, it's crucial to ensure the benchmark data and runners are correct. This is the purpose of the tests in `test_benchmarks.py`.

These tests are not for evaluating candidates; they are for **validating the framework itself**. They work by running the `GroundTruthAnswerGenerator`—which is expected to be perfect—and asserting that it achieves a 100% pass rate. If these tests fail, it indicates a problem with the benchmark definitions or the runners, not the candidate generator.

**To run the validation tests:**
```bash
pytest benchmarks/test_benchmarks.py
```
A successful run is a prerequisite for meaningful evaluation of other answer generators.

### 2. Evaluating Candidate Answer Generators

This is the primary purpose of the framework. The goal is to run one or more experimental `AnswerGenerator`s against the benchmark suites to gather performance metrics. This is not a simple pass/fail test but an experiment to produce a comparative analysis.

The recommended way to do this is to use a separate script or a Jupyter Notebook (see `benchmark_visualization.ipynb` for an example) where you can:
1.  Import your candidate `AnswerGenerator`s.
2.  Call `benchmark_orchestrator.run_benchmarks()` with a list of the generators you want to compare.
3.  Analyze and visualize the resulting pandas DataFrame.

This approach keeps experimental runs separate from the framework's integrity tests.

### Example: Evaluating a Custom Generator

Here is a code snippet demonstrating how to run an evaluation. You can use this as a template for your own evaluation scripts.

First, define your custom generator (e.g., in `my_answer_generator.py`):

```python
# my_answer_generator.py
from benchmarks.answer_generators import AnswerGenerator
from benchmarks.data_models import BaseBenchmarkCase, GeneratedAnswer, FixErrorAnswerOutput

class MySimpleAnswerGenerator(AnswerGenerator):
    """A simple generator that always returns 'pass' for fix_error cases."""
    def generate_answer(self, benchmark_case: BaseBenchmarkCase) -> GeneratedAnswer:
        code_snippet = "pass"  # Replace with your actual generation logic
        output = FixErrorAnswerOutput(code=code_snippet)
        return GeneratedAnswer(output=output)
```

Next, create your evaluation script to run the benchmark:

```python
# run_my_evaluation.py
import asyncio
import pandas as pd
from benchmarks import benchmark_orchestrator
from benchmarks.answer_generators import GroundTruthAnswerGenerator
from my_answer_generator import MySimpleAnswerGenerator

async def main():
    benchmark_suites = [
        "benchmarks/benchmark_definitions/fix_error_benchmarks.yaml",
    ]
    answer_generators_to_test = [
        GroundTruthAnswerGenerator(),
        MySimpleAnswerGenerator(),
    ]

    print("Executing benchmark evaluation...")
    raw_results_df = await benchmark_orchestrator.run_benchmarks(
        benchmark_suites, answer_generators_to_test
    )

    # Calculate summary from raw results
    summary_df = (
        raw_results_df.groupby("answer_generator")["result"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "passed", "count": "total"})
    )
    summary_df["pass_rate"] = summary_df["passed"] / summary_df["total"]

    print("\n--- Evaluation Summary ---")
    print(summary_df)

    print("\n--- Raw Results ---")
    print(raw_results_df)

if __name__ == "__main__":
    asyncio.run(main())
```

Finally, run the script from your terminal:

```bash
python run_my_evaluation.py
```

## Extending the Framework

The framework is designed to be extensible.

### How to Add a New Candidate Answer Generator

1.  **Create the Generator Class:**
    *   In `answer_generators.py`, create a new class that inherits from `AnswerGenerator`.
    *   Implement the `generate_answer(self, benchmark_case: BaseBenchmarkCase) -> str` method.
    *   Inside this method, add logic to handle the different `benchmark_case` types (`FixErrorBenchmarkCase`, `ApiUnderstandingBenchmarkCase`, etc.) and return the generated code as a string.

2.  **Evaluate the Generator:**
    *   In your evaluation script or notebook, import your new generator.
    *   Add an instance of it to the `answer_generators` list that you pass to `benchmark_orchestrator.run_benchmarks()`.

### How to Add a New Benchmark Type

To add a new type of benchmark (e.g., "code_completion"), follow these steps:

1.  **Define the Data Model:**
    *   In `data_models.py`, create a new Pydantic model that inherits from `BaseBenchmarkCase` (e.g., `CodeCompletionBenchmarkCase`).
    *   Add a new value to the `BenchmarkType` enum (e.g., `CODE_COMPLETION = "code_completion"`).
    *   Set the `benchmark_type` field in your new class to `Literal[BenchmarkType.CODE_COMPLETION]`.
    *   Add your new class to the `BenchmarkCase` `Union` type.
    *   Implement the abstract `runner` property to return an instance of your new `BenchmarkRunner` (see next step).

2.  **Implement the Benchmark Runner:**
    *   In `benchmark_runner.py`, create a new class that inherits from `BenchmarkRunner` (e.g., `CodeCompletionRunner`).
    *   Implement the `async def run_benchmark(...)` method to define the execution and validation logic for this new benchmark type. It must return a tuple of `("pass" or "fail", validation_error_string_or_none)`.

3.  **Create the YAML Data File:**
    *   Create a new YAML file in `benchmark_definitions/` (e.g., `code_completion_benchmarks.yaml`).
    *   Populate this file with benchmark cases matching the Pydantic model you created.

4.  **Update Answer Generators:**
    *   In `answer_generators.py`, update the `generate_answer` method in `GroundTruthAnswerGenerator` and any other relevant generators to handle your new `CodeCompletionBenchmarkCase`.

5.  **Add to the Validation Suite:**
    *   In `test_benchmarks.py`, add the path to your new YAML file to the `benchmark_suites` list to include it in the framework's integrity validation run.
