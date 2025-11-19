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
from tqdm.asyncio import tqdm
from benchmarks.data_models import (
    ApiUnderstandingBenchmarkCase,
    BaseBenchmarkCase,
    BenchmarkFile,
    BenchmarkRunResult,
    FixErrorBenchmarkCase,
)
from benchmarks.validation_utils import ValidationError


import time
from typing import Union

async def _run_single_benchmark(
    suite_file: str,
    case: BaseBenchmarkCase,
    generator: AnswerGenerator,
) -> BenchmarkRunResult:
    """Helper coroutine to run one benchmark case and return its result."""
    runner = case.runner
    
    start_time = time.time()
    generated_answer = await generator.generate_answer(case)
    latency = time.time() - start_time
    
    result, validation_error, temp_file_path = await runner.run_benchmark(
        case, generated_answer
    )

    return BenchmarkRunResult(
        suite=Path(suite_file).name,
        benchmark_name=case.get_identifier(),
        answer_generator=generator.name,
        result=1 if result == "pass" else 0,
        answer=str(generated_answer.output),
        validation_error=validation_error,
        temp_test_file=temp_file_path,
        latency=latency,
    )


async def run_benchmarks(
    benchmark_suites: list[str], 
    answer_generators: list[AnswerGenerator]
) -> list[BenchmarkRunResult]:
    """
    Runs all benchmark suites against all answer generators in parallel and returns raw results.
    """
    tasks = []
    
    for suite_file in benchmark_suites:
        print(f"--- Loading benchmark suite: {suite_file} ---")
        with open(suite_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        benchmark_file = BenchmarkFile.model_validate(data)

        for generator in answer_generators:
            print(
                "  - Queuing tests for answer generator:"
                f" {generator.name}"
            )
            for case in benchmark_file.benchmarks:
                tasks.append(_run_single_benchmark(suite_file, case, generator))

    print(f"\n--- Running {len(tasks)} benchmarks in parallel ---")
    results = [
        await f
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks))
    ]

    return results


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
