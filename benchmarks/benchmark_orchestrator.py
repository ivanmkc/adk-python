# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A test rig to validate the benchmarks against the codebase."""

import argparse

import asyncio

import sys

from pathlib import Path


import pandas as pd


import yaml


from benchmarks.answer_generators import (
    AnswerGenerator,
    GroundTruthAnswerGenerator,
    TrivialAnswerGenerator,
)


from benchmarks.benchmark_runner import ApiUnderstandingRunner, PytestBenchmarkRunner
from benchmarks.data_models import (
    ApiUnderstandingBenchmarkCase,
    BenchmarkFile,
    FixErrorBenchmarkCase,
)
from benchmarks.validation_utils import ValidationError


async def run_benchmarks(
    benchmark_suites: list[str], answer_generators: list[AnswerGenerator]
) -> pd.DataFrame:
    """
    Runs all benchmark suites against all answer generators and returns raw results.

    This function serves as the central orchestrator for the benchmark framework.
    It performs the following steps:
      1. Iterates through each provided benchmark suite (YAML file).
      2. For each suite, it iterates through every provided AnswerGenerator.
      3. For each benchmark case within the suite, it determines the appropriate
         BenchmarkRunner.
      4. It invokes the AnswerGenerator to get the code to test.
      5. It calls the selected BenchmarkRunner to execute the test.
      6. It compiles the detailed pass/fail results into a raw DataFrame.

    Args:
      benchmark_suites: A list of paths to the benchmark suite YAML files.
      answer_generators: A list of AnswerGenerator instances to evaluate.

    Returns:
      A pandas DataFrame containing the raw, unsummarized results of the
      benchmark run. Each row includes the suite, benchmark name, answer
      generator, and the pass/fail result.
    """
    results = []

    for suite_file in benchmark_suites:
        print(f"--- Running benchmark suite: {suite_file} ---")
        with open(suite_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        benchmark_file = BenchmarkFile.model_validate(data)

        for generator in answer_generators:
            generator_name = generator.__class__.__name__
            print(f"  - Using answer generator: {generator_name}")
            for case in benchmark_file.benchmarks:
                runner = case.runner
                generated_answer = generator.generate_answer(case)
                result, validation_error = await runner.run_benchmark(
                    case, generated_answer
                )

                results.append(
                    {
                        "suite": Path(suite_file).name,
                        "benchmark_name": case.get_identifier(),
                        "answer_generator": generator_name,
                        "result": 1 if result == "pass" else 0,
                        "answer": str(generated_answer.output),
                        "validation_error": validation_error,
                    }
                )

    return pd.DataFrame(results)


def main():
    """Main entry point for the script."""

    parser = argparse.ArgumentParser(description="Run the benchmark suites.")

    parser.add_argument(
        "benchmark_files",
        type=str,
        nargs="+",
        help="Paths to the benchmark YAML files.",
    )

    args = parser.parse_args()

    answer_generators = [GroundTruthAnswerGenerator(), TrivialAnswerGenerator()]

    if not asyncio.run(run_benchmarks(args.benchmark_files, answer_generators)):

        sys.exit(1)


if __name__ == "__main__":

    main()
