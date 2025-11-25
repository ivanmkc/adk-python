# ADK Benchmark Framework

This directory contains a data-driven framework for evaluating and comparing different code generation strategies, referred to as "Answer Generators."

## Overview

The benchmark framework is orchestrated by `benchmark_orchestrator.py` and initiated by `test_benchmarks.py`. It operates by running `AnswerGenerator` classes against benchmark cases defined in YAML files. The orchestrator runs all tests in parallel and returns a list of strongly-typed `BenchmarkRunResult` Pydantic objects that can be easily converted into a pandas DataFrame for analysis.

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
| data_models.py|  |  answer_generators/  |  | benchmark_runner.py |
+---------------+  +----------------------+  +---------------------+
                      |
                      | Reads from
                      v
        +---------------------------+
        | ground_truth/               |
        +---------------------------+

```

### Key Components

*   **`test_benchmarks.py`**: The main `pytest` entry point for validating the framework's integrity.
*   **`benchmark_orchestrator.py`**: The central orchestrator that runs benchmarks in parallel, calls the appropriate runner for each case, and aggregates results into a list of `BenchmarkRunResult` objects.
*   **`benchmark_runner.py`**: Defines strategies for executing benchmarks (e.g., `PytestBenchmarkRunner`). Each runner creates a persistent temporary file for its test case to allow for inspection after the run.
*   **`answer_generators/`**: A package containing different code generation strategies (e.g., `GroundTruthAnswerGenerator`, `GeminiAnswerGenerator`).
*   **`data_models.py`**: Pydantic models for the benchmark YAML files, structured `AnswerOutput` schemas, and the `BenchmarkRunResult`.
*   **`benchmark_definitions/`**: Contains the YAML data files and test templates.
*   **`ground_truth/`**: Contains the correct code snippets for `fix_error` benchmarks.

## Usage Philosophy

There are two distinct ways to use this framework: validating its integrity and evaluating candidate answer generators.

### 1. Validating the Benchmark Framework

Before running experiments, it's crucial to ensure the benchmark data and runners are correct. This is the purpose of the tests in `test_benchmarks.py`.

These tests are not for evaluating candidates; they are for **validating the framework itself**. They work by running the `GroundTruthAnswerGenerator`—which is expected to be perfect—and asserting that it achieves a 100% pass rate. If these tests fail, it indicates a problem with the benchmark definitions or the runners, not the candidate generator.

**To run the validation tests:**
```bash
env/bin/pytest benchmarks/test_benchmarks.py
```
A successful run is a prerequisite for meaningful evaluation of other answer generators.

### Running Benchmark Tests
To run all the benchmark tests directly, you can use the following command from the root of the project:
```bash
python -m pytest ./benchmarks/
```

### Verification Tools

#### Multiple Choice Leak Checker (`check_mc_leaks.py`)

This script is designed to proactively detect potential "answer leaks" in Multiple Choice (MC) benchmark cases. It uses an LLM to analyze the question, options, correct answer, and the provided code snippet to determine if the snippet or its surrounding context inadvertently reveals the answer, making the question trivial.

**Purpose:**
*   Ensures the integrity and fairness of MC benchmarks.
*   Helps prevent scenarios where the LLM can "game" the system by inferring the answer without actual understanding.

**How it Works:**
1.  The script iterates through all MC benchmark suites (`*_mc/benchmark.yaml`).
2.  For each MC case, it extracts the question, options, correct answer, and the associated code snippet (delimited by `# --8<-- [start:...]` and `# --8<-- [end:...]` tags).
3.  An LLM is prompted to act as a "strict exam proctor" and evaluate if the snippet contains explicit hints, solution patterns, or contextual information that makes the correct answer obvious without requiring deep library knowledge.

**To run the Leak Checker:**
```bash
# Ensure you have the GEMINI_API_KEY environment variable set.
# Example: export GEMINI_API_KEY="YOUR_API_KEY"
env/bin/python benchmarks/verification/check_mc_leaks.py
```

**Important Notes:**
*   The LLM's assessment is based on a heuristic and may require human review.
*   If leaks are detected, it's recommended to refine the benchmark's code snippet or question to ensure true knowledge testing.

### 2. Evaluating Candidate Answer Generators

This is the primary purpose of the framework. The goal is to run one or more experimental `AnswerGenerator`s against the benchmark suites to gather performance metrics. This is not a simple pass/fail test but an experiment to produce a comparative analysis.

The recommended way to do this is to use a separate script or a Jupyter Notebook (see `benchmark_debug.py` for an example) where you can:
1.  Import your candidate `AnswerGenerator`s.
2.  Call `benchmark_orchestrator.run_benchmarks()` with a list of the generators you want to compare.
3.  Convert the resulting list of `BenchmarkRunResult` objects into a pandas DataFrame for analysis and visualization.

This approach keeps experimental runs separate from the framework's integrity tests.

### Example: Evaluating a Custom Generator

Here is a code snippet demonstrating how to run an evaluation. You can use this as a template for your own evaluation scripts.

First, define your custom generator. For a sophisticated example, see `benchmarks/answer_generators/gemini_answer_generator.py`, which calls the Gemini API to generate code. You will need to set the `GEMINI_API_KEY` environment variable for it to work.

Next, create your evaluation script to run the benchmark:

```python
# run_my_evaluation.py
import asyncio
import pandas as pd
from benchmarks import benchmark_orchestrator
from benchmarks.answer_generators import (
    GroundTruthAnswerGenerator,
    TrivialAnswerGenerator,
    GeminiAnswerGenerator,
)

async def main():
    benchmark_suites = [
        "benchmarks/benchmark_definitions/fix_errors/benchmark.yaml",
        "benchmarks/benchmark_definitions/api_understanding/benchmark.yaml",
    ]
    answer_generators_to_test = [
        GroundTruthAnswerGenerator(),
        TrivialAnswerGenerator(),
        GeminiAnswerGenerator(),
    ]

    print("Executing benchmark evaluation...")
    results = await benchmark_orchestrator.run_benchmarks(
        benchmark_suites, answer_generators_to_test
    )
    raw_results_df = pd.DataFrame([r.model_dump() for r in results])

    # Calculate summary from raw results
    summary_df = (
        raw_results_df.groupby(["answer_generator", "result_type"])
        .size()
        .unstack(fill_value=0)
    )
    
    # Calculate pass rate if 'pass' column exists
    if "pass" in summary_df.columns:
        summary_df["total"] = summary_df.sum(axis=1)
        summary_df["pass_rate"] = summary_df["pass"] / summary_df["total"]
    else:
        summary_df["total"] = summary_df.sum(axis=1)
        summary_df["pass_rate"] = 0.0

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

## Result Types

The framework distinguishes between different types of results to provide deeper insights into generator performance:

*   **`PASS`**: The generated code ran successfully and passed all assertions/validations.
*   **`FAIL_VALIDATION`**: The generated code ran successfully but failed the assertions (e.g., produced the wrong answer). This indicates a logic error in the generated solution.
*   **`FAIL_CRASH`**: The generated code could not be executed or crashed during execution (e.g., `SyntaxError`, `ImportError`, `NameError`). This indicates that the generated code is syntactically invalid or references non-existent symbols.

## Extending the Framework

The framework is designed to be extensible.

### How to Add a New Candidate Answer Generator

1.  **Create the Generator Class:**
    *   In `benchmarks/answer_generators/`, create a new module and class that inherits from `AnswerGenerator`.
    *   Implement the `generate_answer(self, benchmark_case: BaseBenchmarkCase) -> GeneratedAnswer` method.
    *   Inside this method, add logic to handle the different `benchmark_case` types (e.g. `FixErrorBenchmarkCase`) and return a `GeneratedAnswer` containing the appropriate `AnswerOutput` (e.g. `FixErrorAnswerOutput`).

2.  **Evaluate the Generator:**
    *   In your evaluation script or notebook, import your new generator.
    *   Add an instance of it to the `answer_generators` list that you pass to `benchmark_orchestrator.run_benchmarks()`.

### How to Add a New Benchmark Type

To add a new type of benchmark (e.g., "code_completion"), follow these steps:

1.  **Define the Data Models:**
    *   In `data_models.py`, create a new Pydantic model that inherits from `BaseBenchmarkCase` (e.g., `CodeCompletionBenchmarkCase`).
    *   Create a new output model inheriting from `BaseAnswerOutput` (e.g. `CodeCompletionAnswerOutput`).
    *   Add a new value to the `BenchmarkType` enum (e.g., `CODE_COMPLETION = "code_completion"`).
    *   Set the `benchmark_type` field in your new classes to `Literal[BenchmarkType.CODE_COMPLETION]`.
    *   Add your new classes to the `BenchmarkCase` and `AnswerOutput` `Union` types.
    *   Implement the abstract `runner` property in your case class to return an instance of your new `BenchmarkRunner`.

2.  **Implement the Benchmark Runner:**
    *   In `benchmark_runner.py`, create a new class that inherits from `BenchmarkRunner` (e.g., `CodeCompletionRunner`).
    *   Implement the `async def run_benchmark(...)` method to define the execution and validation logic. It must return a tuple of `(result: str, validation_error: Optional[str], temp_file_path: Optional[str])`.

3.  **Create the YAML Data File:**
    *   Create a new YAML file in `benchmark_definitions/` (e.g., `code_completion_benchmarks.yaml`).
    *   Populate this file with benchmark cases matching the Pydantic model you created.

4.  **Update Answer Generators:**
    *   Update the `generate_answer` method in `GroundTruthAnswerGenerator` and any other relevant generators to handle your new `CodeCompletionBenchmarkCase` and return a `GeneratedAnswer` wrapping `CodeCompletionAnswerOutput`.

5.  **Add to the Validation Suite:**
    *   In `test_benchmarks.py`, add the path to your new YAML file to the `benchmark_suites` list to include it in the framework's integrity validation run.

### `fix_error` Benchmark Requirements

When creating a `fix_error` benchmark case, the goal is to test the LLM's ability to solve a problem based on a description of the requirements, not its ability to simply pass a test.

To this end, the test's assertions should be translated into natural language requirements that are passed to the model in the prompt. **Do not include the test code itself in the prompt.**

**Example:**

*   **Instead of**: Providing the test code with `assert "test" in response.lower()`.
*   **Do**: Provide a natural language requirement like: "The agent's final response must contain the word 'test'."

This approach prevents the model from "gaming" the benchmark and encourages it to generate code that solves the underlying problem.

### Structuring `fix_error` YAML

To implement this, the YAML definition for a `fix_error` case should be structured to separate the high-level task description and natural language requirements from the test implementation.

A robust way to implement this is to use special comments or tags within the test file to explicitly mark the sections of code that should be passed to the LLM as context.

#### Bad Example (Legacy Approach)

This example is not ideal because the description is generic and it implicitly sends the entire test file to the LLM, including the assertion logic which can be "gamed".

```yaml
- name: "02: An LlmAgent with a simple function tool."
  description: "02: An LlmAgent with a simple function tool." # Vague description
  benchmark_type: fix_error
  test_file: benchmarks/benchmark_definitions/fix_errors/tests/test_02_agent_with_tool.py
  # Implicitly sends the whole file, including the test assertions.
```

#### Good Example (Recommended Approach)

This structure provides clear, natural language requirements. The YAML configuration specifies the test file, a high-level description of the task, and a list of specific requirements that the generated code must meet.

```yaml
- name: "02: An LlmAgent with a simple function tool."
  benchmark_type: fix_error
  test_file: benchmarks/benchmark_definitions/fix_errors/tests/test_02_agent_with_tool.py
  description: "Create a minimal LlmAgent named 'root_agent' that can use the `basic_tool`."
  requirements:
    - "When asked 'Can you use your tool?', the agent should use the `basic_tool` with the query 'test'."
    - "The agent's final response must contain the word 'test'."
```

The benchmark runner will then extract the relevant code context from the `test_file` by looking for special tags. This ensures that test-specific logic, like assertions, is not shown to the model.

For example, the corresponding test file would be structured with tags like `# LLM_CONTEXT_BEGIN` and `# LLM_CONTEXT_END` to delineate the context.

```python
# test_02_agent_with_tool.py

# LLM_CONTEXT_BEGIN
"""02: An LlmAgent with a simple function tool."""

from __future__ import annotations

from google.adk.agents import LlmAgent
from benchmarks.test_helpers import MODEL_NAME, basic_tool

# The LLM is expected to fill in the code between BEGIN: CODE and END: CODE
# BEGIN: CODE
# END: CODE
# LLM_CONTEXT_END

# This part of the file, containing the test runner and assertions,
# is excluded from the LLM's view.
async def run_test() -> str:
    ...

def assert_test(response: str):
    ...
```

### Multiple Choice (MC) Benchmarks

For multiple-choice benchmarks (e.g., `predict_runtime_behavior_mc`), strict context isolation is critical to prevent "leaking" the answer to the model. The `# LLM_CONTEXT_BEGIN` and `# LLM_CONTEXT_END` markers must strictly wrap **only** the code snippet being tested.

**Example of an MC case:**

```python
# test_case_01.py

# LLM_CONTEXT_BEGIN
def code_under_test():
   # Code that demonstrates the behavior in question
   agent = LlmAgent(name="test")
   agent.name = "new_name"
# LLM_CONTEXT_END

def test_agent_name_mutability():
    """
    Validates that agent name is mutable.
    """
    # ... Assertion logic (HIDDEN FROM LLM) ...
```

The framework extracts only the content between the markers to form the prompt, ensuring the model predicts the behavior based solely on the code, without seeing the test's assertions or comments that might reveal the answer.
