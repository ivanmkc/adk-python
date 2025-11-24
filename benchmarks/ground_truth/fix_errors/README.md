# Ground Truth Answers

This directory contains the ground truth answers for the `fix_error` benchmark suite. Each file in this directory corresponds to a test template in `benchmarks/benchmark_definitions/fix_error/` and contains the correct, working code snippet that should pass the test.

## Structure

Each file is a complete Python test file with the correct code injected into the `# BEGIN: CODE...# END: CODE` block.

## Usage

The `GroundTruthAnswerGenerator` uses the files in this directory to provide a "perfect" answer for each `fix_error` benchmark case. When the benchmark framework is run with the `GroundTruthAnswerGenerator`, it is expected to achieve a 100% pass rate.

This serves as a crucial validation step for the framework itself. If the `GroundTruthAnswerGenerator` fails, it indicates a problem with the benchmark definitions, the test templates, or the benchmark runners, rather than a failure of the answer generator.

## Running Tests

You can run the ground truth tests for the `fix_errors` benchmark suite directly using:
```bash
python -m pytest ./benchmarks/ground_truth/fix_errors/
```

To add a new ground truth answer:
1. Create a new `fix_error` test template in `benchmarks/benchmark_definitions/fix_error/`.
2. Create a corresponding file in this directory with the same name.
3. In the new file, add the correct, working code snippet that will make the test pass.
