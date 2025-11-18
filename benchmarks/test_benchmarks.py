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

"""Master test file for running all benchmarks."""

import pytest
from benchmarks.answer_generators import (
    GroundTruthAnswerGenerator,
    TrivialAnswerGenerator,
)
from benchmarks import benchmark_orchestrator


@pytest.mark.asyncio
async def test_benchmarks():
  """
  Runs a comprehensive benchmark test suite.

  This test evaluates multiple answer generators against all available benchmark
  suites (both 'fix_error' and 'api_understanding'). Its primary assertion is
  that the GroundTruthAnswerGenerator achieves a perfect score (100% pass rate),
  which validates the integrity of the benchmark framework itself.
  """
  benchmark_suites = [
      "benchmarks/benchmark_definitions/api_understanding_benchmarks.yaml",
      "benchmarks/benchmark_definitions/fix_error_benchmarks.yaml",
  ]
  answer_generators = [GroundTruthAnswerGenerator(), TrivialAnswerGenerator()]
  summary_df = await benchmark_orchestrator.run_benchmarks(benchmark_suites, answer_generators)

  print("\n--- Benchmark Summary ---")
  print(summary_df)

  ground_truth_pass_rate = summary_df.loc["GroundTruthAnswerGenerator"][
      "pass_rate"
  ]
  assert ground_truth_pass_rate == 1.0, (
      "GroundTruthAnswerGenerator failed to achieve a perfect score."
  )

  trivial_pass_rate = summary_df.loc["TrivialAnswerGenerator"]["pass_rate"]
  assert trivial_pass_rate == 0.0, (
      "TrivialAnswerGenerator achieved a non-zero score."
  )
