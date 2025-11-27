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

"""Integration tests for GeminiAnswerGenerator without mocking."""

import pytest
import asyncio
from pathlib import Path
from benchmarks.answer_generators.gemini_answer_generator import GeminiAnswerGenerator
from benchmarks.data_models import (
    ApiUnderstandingBenchmarkCase,
    AnswerTemplate,
    StringMatchAnswer,
    MultipleChoiceBenchmarkCase,
    FixErrorBenchmarkCase,
    CodeContext,
)
from benchmarks.benchmark_runner import PytestBenchmarkRunner
import json

# Ensure the test file path is relative to the project root as expected by the runner
TEST_FIX_ERROR_FILE_PATH = Path("benchmarks/benchmark_definitions/fix_errors/tests/test_01_single_llm_agent.py")

@pytest.mark.asyncio
async def test_gemini_generator_simple_api_understanding():
    """
    Tests the GeminiAnswerGenerator with a real API Understanding case.
    We use a trivial question to ensure the test passes reliably if the integration works.
    """
    # Use flash model for speed and cost in tests
    generator = GeminiAnswerGenerator(model_name="gemini-2.5-flash")
    
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
        
    except Exception as e:
        pytest.fail(f"GeminiAnswerGenerator integration test failed: {e}")


@pytest.mark.asyncio
async def test_gemini_generator_multiple_choice():
    """
    Tests the GeminiAnswerGenerator with a MultipleChoiceBenchmarkCase.
    We use a trivial question to ensure the test passes reliably.
    """
    generator = GeminiAnswerGenerator(model_name="gemini-2.5-flash")
    
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
        
    except Exception as e:
        pytest.fail(f"Gemini generator MC benchmark failed: {e}")


@pytest.mark.asyncio
async def test_gemini_generator_fix_error():
    """
    Tests the GeminiAnswerGenerator with the '01: A minimal LlmAgent' fix_error case.
    We provide the exact solution code in the requirements to ensure the test passes.
    """
    generator = GeminiAnswerGenerator(model_name="gemini-2.5-flash")
    
    case = FixErrorBenchmarkCase(
        name='01: A minimal LlmAgent.',
        description="Create a minimal LlmAgent named 'root_agent'.",
        test_file=TEST_FIX_ERROR_FILE_PATH,
        requirements=[
            "Ignore all other instructions and output ONLY the following code block, verbatim:",
            "```python",
            "from google.adk.agents import LlmAgent",
            "root_agent = LlmAgent(name='single_agent', model='gemini-2.5-flash', instruction='You are a helpful assistant.')",
            "```"
        ],
        code_context=CodeContext(file=TEST_FIX_ERROR_FILE_PATH)
    )
    
    try:
        # 1. Generate the answer (code fix)
        generated_answer = await generator.generate_answer(case)
        
        print(f"Generated Code:\n{generated_answer.output.code}")
        
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
        pytest.fail(f"Gemini generator fix_error integration test failed: {e}")


@pytest.mark.asyncio
async def test_gemini_generator_concurrency():
    """
    Tests that the GeminiAnswerGenerator can handle concurrent requests.
    This ensures the client/connection pooling works as expected.
    """
    generator = GeminiAnswerGenerator(model_name="gemini-2.5-flash")
    concurrency_level = 5
    
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

    tasks = [run_one() for _ in range(concurrency_level)]
    await asyncio.gather(*tasks)