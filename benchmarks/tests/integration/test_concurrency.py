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

"""Integration tests for concurrency/parallel execution of generators."""

import asyncio
import pytest
from pathlib import Path
from benchmarks.answer_generators.base import AnswerGenerator
from benchmarks.benchmark_candidates import CANDIDATE_GENERATORS
from benchmarks.data_models import (
    ApiUnderstandingBenchmarkCase,
    AnswerTemplate,
    StringMatchAnswer,
)

@pytest.mark.asyncio
@pytest.mark.parametrize("generator", CANDIDATE_GENERATORS, ids=lambda g: g.name)
async def test_generator_concurrency(generator: AnswerGenerator):
    """
    Tests that a generator can handle concurrent requests without collision or failure.
    This is critical for the benchmark orchestrator which runs cases in parallel.
    
    Specifically catches issues like hardcoded session IDs in AdkAnswerGenerator.
    """
    concurrency_level = 5
    
    # A trivial case that requires minimal processing but exercises the full pipeline
    case = ApiUnderstandingBenchmarkCase(
        name="Concurrency Test",
        description="Concurrency Test",
        category="Core",
        question="Return `class Trivial:` and FQN `trivial.Trivial`.",
        rationale="Trivial.",
        file=Path("src/google/adk/events/event.py"), 
        template=AnswerTemplate.CLASS_DEFINITION,
        answers=[
            StringMatchAnswer(
                answer="class Trivial:",
                fully_qualified_class_name=["trivial.Trivial"],
                answer_template="StringMatchAnswer"
            )
        ]
    )

    async def run_one():
        # We don't strictly check the correctness of the answer here,
        # but we MUST ensure it doesn't raise an exception (like SessionExists).
        try:
            await generator.generate_answer(case)
        except Exception as e:
            pytest.fail(f"Concurrent run failed for {generator.name}: {e}")

    # Run concurrently
    tasks = [run_one() for _ in range(concurrency_level)]
    await asyncio.gather(*tasks)
