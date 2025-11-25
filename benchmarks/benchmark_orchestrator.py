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

import asyncio
from pathlib import Path
import time
from typing import List
from typing import Optional

import tenacity
from tqdm.asyncio import tqdm
import yaml

from benchmarks.answer_generators import AnswerGenerator
from benchmarks.benchmark_runner import ApiUnderstandingRunner
from benchmarks.benchmark_runner import PytestBenchmarkRunner
from benchmarks.data_models import BaseBenchmarkCase
from benchmarks.data_models import BenchmarkFile
from benchmarks.data_models import BenchmarkResultType
from benchmarks.data_models import BenchmarkRunResult
from benchmarks.logger import BenchmarkLogger


async def _run_single_benchmark(
    suite_file: str,
    case: BaseBenchmarkCase,
    generator: AnswerGenerator,
    semaphore: asyncio.Semaphore,
    logger: BenchmarkLogger,
    max_retries: int,
    min_wait: float,
    max_wait: float,
) -> BenchmarkRunResult:
    """Helper coroutine to run one benchmark case and return its result."""
    async with semaphore:
        runner = case.runner

        generated_answer = None
        prompt_content = ""

        start_time = time.time()
        try:
            retryer = tenacity.AsyncRetrying(
                stop=tenacity.stop_after_attempt(max_retries),
                wait=tenacity.wait_exponential(
                    multiplier=1, min=min_wait, max=max_wait
                ),
                retry=tenacity.retry_if_exception_type(Exception),
                reraise=True,
            )

            async for attempt in retryer:
                with attempt:
                    generated_answer = await generator.generate_answer(
                        case
                    )

        except Exception as e:
            error_message = f"Generation failed after {max_retries} retries: {e}"
            if logger:
                logger.log_generation_failure(
                    benchmark_name=case.get_identifier(),
                    error_message=error_message,
                    prompt="",
                )
                
            return BenchmarkRunResult(
                suite=str(Path(suite_file).absolute()),
                benchmark_name=case.get_identifier(),
                answer_generator=generator.name,
                result_type=BenchmarkResultType.FAIL_CRASH,
                result=0,
                answer="",
                validation_error=error_message,
                temp_test_file=None,
                latency=time.time() - start_time,
            )

        latency = time.time() - start_time

        result, validation_error, temp_file_path = await runner.run_benchmark(
            case, generated_answer
        )

        if logger:
            logger.log_test_result(
                benchmark_name=case.get_identifier(),
                result=result,
                validation_error=validation_error,
                temp_test_file=Path(temp_file_path) if temp_file_path else None,
            )

    return BenchmarkRunResult(
        suite=str(Path(suite_file).absolute()),
        benchmark_name=case.get_identifier(),
        answer_generator=generator.name,
        result_type=result,
        result=1 if result == BenchmarkResultType.PASS else 0,
        answer=str(generated_answer.output),
        rationale=(
            generated_answer.output.rationale if generated_answer.output else None
        ),
        validation_error=validation_error,
        temp_test_file=temp_file_path,
        latency=latency,
    )


async def run_benchmarks(
    benchmark_suites: List[str],
    answer_generators: List[AnswerGenerator],
    max_concurrency: int = 50,
    max_retries: int = 7,
    min_wait: float = 4.0,
    max_wait: float = 60.0,
    logger: Optional[BenchmarkLogger] = None,
) -> List[BenchmarkRunResult]:
    """
    Runs all benchmark suites against all answer generators in parallel and returns raw results.
    """
    semaphore = asyncio.Semaphore(max_concurrency)
    tasks = []

    for suite_file in benchmark_suites:
        print(f"--- Loading benchmark suite: {suite_file} ---")
        with open(suite_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        benchmark_file = BenchmarkFile.model_validate(data)

        for generator in answer_generators:
            print("  - Queuing tests for answer generator:" f" {generator.name}")
            for case in benchmark_file.benchmarks:
                tasks.append(
                    _run_single_benchmark(
                        suite_file,
                        case,
                        generator,
                        semaphore,
                        logger,
                        max_retries,
                        min_wait,
                        max_wait,
                    )
                )

    print(
        f"\n--- Running {len(tasks)} benchmarks in parallel (max_concurrency={max_concurrency}) ---\n"
    )
    results = [await f for f in tqdm(asyncio.as_completed(tasks), total=len(tasks))]

    if logger:
        logger.finalize_run()
    return results
