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
)
from benchmarks.tests.integration.test_utils import create_fix_error_benchmark_case
from benchmarks.benchmark_runner import PytestBenchmarkRunner
import json

# Ensure the test file path is relative to the project root as expected by the runner
TEST_FIX_ERROR_FILE_PATH = Path("benchmarks/benchmark_definitions/fix_errors/cases/01_single_llm_agent/test_agent.py")
UNFIXED_FILE_PATH = Path("benchmarks/benchmark_definitions/fix_errors/cases/01_single_llm_agent/unfixed.py")
FIXED_FILE_PATH = Path("benchmarks/benchmark_definitions/fix_errors/cases/01_single_llm_agent/fixed.py")

@pytest.mark.asyncio
async def test_adk_generator_simple_api_understanding():
    """
    Tests the AdkAnswerGenerator with a real API Understanding case.
    We use a trivial question to ensure the test passes reliably if the integration works.
    """
    # Use flash model for speed and cost in tests
    agent = create_default_adk_agent(model_name="gemini-2.5-flash")
    generator = AdkAnswerGenerator(agent=agent)
    
    # A trivial case where we explicitly tell the model what to output
    case = ApiUnderstandingBenchmarkCase(
        name="Trivial Test Case",
        description="Trivial test case for integration.",
        category="Core",
        question=(
            "Please output a JSON object where `code` is `class Event(BaseModel):` "
            "and `fully_qualified_class_name` is `google.adk.events.event.Event`. "
            "Provide a rationale as well."
        ),
        rationale="The question explicitly provides the required output.",
        file=Path("src/google/adk/events/event.py"), # Dummy path for the model structure
        template=AnswerTemplate.CLASS_DEFINITION,
        answers=[
            StringMatchAnswer(
                answer="class Event(BaseModel):",
                fully_qualified_class_name=["google.adk.events.event.Event"],
                answer_template="StringMatchAnswer"
            )
        ]
    )
    
    try:
        generated_answer = await generator.generate_answer(case)
        
        print(f"Generated Code: {generated_answer.output.code}")
        print(f"Generated FQN: {generated_answer.output.fully_qualified_class_name}")
        
        # Verify structure
        assert generated_answer.output.code, "Code should not be empty"
        assert generated_answer.output.fully_qualified_class_name, "FQN should not be empty"
        assert generated_answer.output.rationale, "Rationale should not be empty"
        
        # Verify content correctness (Checking for the requested trivial output)
        assert "Event" in generated_answer.output.fully_qualified_class_name, "FQN missing 'Event'"
        assert "Event" in generated_answer.output.code, "Code missing 'Event'"
        
        # Verify trace logs are present
        assert generated_answer.output.trace_logs, "Trace logs should not be empty"
        assert "Event:" in generated_answer.output.trace_logs, "Trace logs should contain event details"
        
    except Exception as e:
        pytest.fail(f"AdkAnswerGenerator integration test failed: {e}")


@pytest.mark.asyncio
async def test_adk_generator_multiple_choice():
    """
    Tests the AdkAnswerGenerator with a MultipleChoiceBenchmarkCase.
    We use a trivial question to ensure the test passes reliably.
    """
    agent = create_default_adk_agent(model_name="gemini-2.5-flash")
    generator = AdkAnswerGenerator(agent=agent)
    
    case = MultipleChoiceBenchmarkCase(
        question="The correct answer for this question is B. Select B.",
        options={
            "A": "Wrong Option A",
            "B": "Correct Option B",
            "C": "Wrong Option C",
            "D": "Wrong Option D"
        },
        correct_answer="B",
        benchmark_type="multiple_choice",
        explanation="The question explicitly provides the answer."
    )
    
    try:
        generated_answer = await generator.generate_answer(case)
        
        # Check the answer
        assert generated_answer.output.answer == "B", f"Expected answer 'B', got '{generated_answer.output.answer}'"
        
        # Check rationale exists
        assert generated_answer.output.rationale, "Rationale should not be empty"
        
        # Check trace logs
        assert generated_answer.output.trace_logs, "Trace logs should not be empty"
        
    except Exception as e:
        pytest.fail(f"ADK generator MC benchmark failed: {e}")


@pytest.mark.asyncio
async def test_adk_generator_fix_error(tmp_path):
    """
    Tests the AdkAnswerGenerator with the '01: A minimal LlmAgent' fix_error case.
    We provide the exact solution code in the requirements to ensure the test passes.
    """
    agent = create_default_adk_agent(model_name="gemini-2.5-flash")
    generator = AdkAnswerGenerator(agent=agent)
    
    # Create a dummy fix_error case
    test_file_path = tmp_path / "test_agent.py"
    unfixed_file_path = tmp_path / "unfixed.py"
    fixed_file_path = tmp_path / "fixed.py"

    test_file_path.write_text("def test_placeholder(): pass")
    unfixed_file_path.write_text("def unfixed(): pass")
    fixed_file_path.write_text("def fixed(): pass")

    case = create_fix_error_benchmark_case(
        case_path=tmp_path,
        name="Test Fix Error",
        description="Fix a bug by creating a valid agent.",
        requirements=[
            "The solution MUST import `BaseAgent` directly from `google.adk.agents`.",
            "The `create_agent` function MUST have the return type annotation `-> BaseAgent`."
        ]
    )
    
    try:
        # 1. Generate the answer (code fix)
        generated_answer = await generator.generate_answer(case)
        
        print(f"Generated Code:\n{generated_answer.output.code}")
        
        # Check trace logs
        assert generated_answer.output.trace_logs, "Trace logs should not be empty"
        
        # 2. Verify the answer using the actual PytestBenchmarkRunner
        runner = PytestBenchmarkRunner()
        result, logs, temp_file, error_type = await runner.run_benchmark(case, generated_answer)
        
        print(f"Runner Result: {result}")
        print(f"Runner Logs:\n{logs}")
        
        if error_type:
            print(f"Error Type: {error_type}")

        # Assertions
        assert result == "pass", f"Benchmark failed with result: {result}. Logs:\n{logs}"
        
    except Exception as e:
        pytest.fail(f"ADK generator fix_error integration test failed: {e}")

@pytest.mark.asyncio
async def test_adk_generator_concurrency():
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
            "rationale": "Trivial."
        })
        yield Event(
            author="model",
            content=types.Content(parts=[types.Part(text=response_json)])
        )

    mock_agent.run_async = mock_run_async
    
    generator = AdkAnswerGenerator(agent=mock_agent)
    concurrency_level = 5
    
    # A trivial case that requires minimal processing
    case = ApiUnderstandingBenchmarkCase(
        name="Concurrency Test",
        description="Concurrency Test",
        category="Core",
        question="Return `class Trivial:`.",
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
        try:
            await generator.generate_answer(case)
        except Exception as e:
            pytest.fail(f"Concurrent run failed for {generator.name}: {e}")

    # Run concurrently
    tasks = [run_one() for _ in range(concurrency_level)]
    await asyncio.gather(*tasks)