# Benchmark Definitions

This directory contains the YAML files that define the benchmark suites for the ADK Benchmark Framework. Each YAML file represents a collection of benchmark cases that the framework can run.

## Structure

- **`api_understanding_benchmarks.yaml`**: This suite contains benchmarks that test an AI's understanding of the ADK's public API. Each case consists of a question about the API, the expected code snippet as an answer, and metadata for validation.

- **`fix_error_benchmarks.yaml`**: This suite contains benchmarks that evaluate an AI's ability to fix broken code snippets. Each case points to a test file in the `fix_error` directory that is intentionally broken.

- **`fix_error/`**: This subdirectory contains the template files for the `fix_error` benchmark cases. Each file has a placeholder (`# BEGIN: CODE...# END: CODE`) where the AI-generated code will be injected.

## Usage

To run a benchmark suite, you provide the path to its YAML file to the `benchmark_orchestrator.run_benchmarks()` function (typically called from a script like `benchmark_debug.py` or `test_benchmarks.py`). The orchestrator will then parse the file and execute each benchmark case against the specified answer generators.

To add a new benchmark suite, create a new YAML file in this directory following the structure of the existing files.
