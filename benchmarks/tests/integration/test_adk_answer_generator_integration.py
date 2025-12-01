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

"""Integration tests for AdkAnswerGenerator without mocking."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from google.adk.agents import Agent
from google.adk.events import Event
from google.genai import types
from benchmarks.answer_generators.adk_answer_generator import AdkAnswerGenerator
from benchmarks.answer_generators.adk_agents import create_default_adk_agent
from benchmarks.data_models import (
    ApiUnderstandingBenchmarkCase,
    MultipleChoiceBenchmarkCase,
    AnswerTemplate,
    StringMatchAnswer,
    BenchmarkType,
    TraceLogEvent,
)
from benchmarks.tests.integration.test_utils import setup_fix_error_case
from benchmarks.tests.integration.predefined_cases import (
    SIMPLE_API_UNDERSTANDING_CASE,
    SIMPLE_MULTIPLE_CHOICE_CASE,
    CONCURRENCY_TEST_CASE,
    FIX_ERROR_MINIMAL_AGENT_CONTENT,
)
from benchmarks.benchmark_runner import PytestBenchmarkRunner
import json

# Ensure the test file path is relative to the project root as expected by the runner
TEST_FIX_ERROR_FILE_PATH = Path(
    "benchmarks/benchmark_definitions/fix_errors/cases/01_single_llm_agent/test_agent.py"
)
UNFIXED_FILE_PATH = Path(
    "benchmarks/benchmark_definitions/fix_errors/cases/01_single_llm_agent/unfixed.py"
)
FIXED_FILE_PATH = Path(
    "benchmarks/benchmark_definitions/fix_errors/cases/01_single_llm_agent/fixed.py"
)


@pytest.mark.parametrize("case", [SIMPLE_API_UNDERSTANDING_CASE])
@pytest.mark.asyncio
async def test_adk_generator_simple_api_understanding(
    case: ApiUnderstandingBenchmarkCase,
):
  """
  Tests the AdkAnswerGenerator with a real API Understanding case.
  We use a trivial question to ensure the test passes reliably if the integration works.
  """
  # Use flash model for speed and cost in tests
  agent = create_default_adk_agent(model_name="gemini-2.5-flash")
  generator = AdkAnswerGenerator(agent=agent)

  try:
    generated_answer = await generator.generate_answer(case)

    # Verify structure
    assert generated_answer.output.code, "Code should not be empty"
    assert (
        generated_answer.output.fully_qualified_class_name
    ), "FQN should not be empty"
    assert generated_answer.output.rationale, "Rationale should not be empty"

    # Verify content correctness (Checking for the requested trivial output)
    assert (
        "Event" in generated_answer.output.fully_qualified_class_name
    ), "FQN missing 'Event'"
    assert "Event" in generated_answer.output.code, "Code missing 'Event'"

    # Verify trace logs are present
    assert generated_answer.trace_logs, "Trace logs should not be empty"
    assert all(
        isinstance(log_entry, TraceLogEvent)
        for log_entry in generated_answer.trace_logs
    ), "All trace log entries should be TraceLogEvent objects"
    assert any(
        log_entry.type == "ADK_EVENT"
        for log_entry in generated_answer.trace_logs
    ), "Trace logs should contain ADK_EVENT type"

  except Exception as e:
    pytest.fail(f"AdkAnswerGenerator integration test failed: {e}")


@pytest.mark.parametrize("case", [SIMPLE_MULTIPLE_CHOICE_CASE])
@pytest.mark.asyncio
async def test_adk_generator_multiple_choice(case: MultipleChoiceBenchmarkCase):
  """
  Tests the AdkAnswerGenerator with a MultipleChoiceBenchmarkCase.
  We use a trivial question to ensure the test passes reliably.
  """
  agent = create_default_adk_agent(model_name="gemini-2.5-flash")
  generator = AdkAnswerGenerator(agent=agent)

  try:
    generated_answer = await generator.generate_answer(case)

    # Check the answer
    assert (
        generated_answer.output.answer == "B"
    ), f"Expected answer 'B', got '{generated_answer.output.answer}'"

    # Check trace logs
    assert generated_answer.trace_logs, "Trace logs should not be empty"
    assert all(
        isinstance(log_entry, TraceLogEvent)
        for log_entry in generated_answer.trace_logs
    ), "All trace log entries should be TraceLogEvent objects"
    assert any(
        log_entry.type == "ADK_EVENT"
        for log_entry in generated_answer.trace_logs
    ), "Trace logs should contain ADK_EVENT type"

  except Exception as e:
    pytest.fail(f"ADK generator MC benchmark failed: {e}")


@pytest.mark.parametrize("fix_error_content", [FIX_ERROR_MINIMAL_AGENT_CONTENT])
@pytest.mark.asyncio
async def test_adk_generator_fix_error(tmp_path, fix_error_content):
  """
  Tests the AdkAnswerGenerator with the '01: A minimal LlmAgent' fix_error case.
  We provide the exact solution code in the requirements to ensure the test passes.
  """
  agent = create_default_adk_agent(model_name="gemini-2.5-flash")
  generator = AdkAnswerGenerator(agent=agent)

  case = setup_fix_error_case(tmp_path, fix_error_content)

  try:
    # 1. Generate the answer (code fix)
    generated_answer = await generator.generate_answer(case)

    # Check trace logs
    assert generated_answer.trace_logs, "Trace logs should not be empty"
    assert all(
        isinstance(log_entry, TraceLogEvent)
        for log_entry in generated_answer.trace_logs
    ), "All trace log entries should be TraceLogEvent objects"
    assert any(
        log_entry.type == "ADK_EVENT"
        for log_entry in generated_answer.trace_logs
    ), "Trace logs should contain ADK_EVENT type"

    # 2. Verify the answer using the actual PytestBenchmarkRunner
    runner = PytestBenchmarkRunner()
    result, logs, temp_file, error_type = await runner.run_benchmark(
        case, generated_answer
    )

    # Assertions
    assert (
        result == "pass"
    ), f"Benchmark failed with result: {result}. Logs:\n{logs}"

  except Exception as e:
    pytest.fail(f"ADK generator fix_error integration test failed: {e}")


@pytest.mark.parametrize("case", [CONCURRENCY_TEST_CASE])
@pytest.mark.asyncio
async def test_adk_generator_concurrency(case: ApiUnderstandingBenchmarkCase):
  """
  Tests that the AdkAnswerGenerator can handle concurrent requests without collision.
  This ensures session IDs are unique per call.
  """
  # Create a mock agent that returns a valid JSON response
  mock_agent = MagicMock(spec=Agent)
  mock_agent.name = "mock_concurrency_agent"

  # Mock run_async to yield a response event
  async def mock_run_async(*args, **kwargs):
    response_json = json.dumps({
        "code": "class Trivial:",
        "fully_qualified_class_name": "trivial.Trivial",
        "rationale": "Trivial.",
    })
    yield Event(
        author="model",
        content=types.Content(parts=[types.Part(text=response_json)]),
    )

  mock_agent.run_async = mock_run_async

  generator = AdkAnswerGenerator(agent=mock_agent)
  concurrency_level = 5

  async def run_one():
    try:
      await generator.generate_answer(case)
    except Exception as e:
      pytest.fail(f"Concurrent run failed for {generator.name}: {e}")

  # Run concurrently
  tasks = [run_one() for _ in range(concurrency_level)]
  await asyncio.gather(*tasks)
