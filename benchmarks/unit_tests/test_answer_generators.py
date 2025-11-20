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

"""Unit tests for the answer generators."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import sys
from pathlib import Path

# Ensure src is in path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from benchmarks.answer_generators import (
    AdkAnswerGenerator,
    GeminiAnswerGenerator,
    GroundTruthAnswerGenerator,
    TrivialAnswerGenerator,
)
from benchmarks.data_models import (
    ApiUnderstandingBenchmarkCase,
    StringMatchAnswer,
    AnswerTemplate,
)
from google.genai import types
from google.adk.events.event import Event # Added import


@pytest.fixture
def mock_api_case() -> ApiUnderstandingBenchmarkCase:
    """Returns a mock ApiUnderstandingBenchmarkCase for testing."""
    return ApiUnderstandingBenchmarkCase(
        name="Test Case",
        description="A test case.",
        question="What is the class for a session?",
        rationale="To test the generator.",
        category="Data Models",
        file=Path("src/google/adk/sessions/session.py"),
        template=AnswerTemplate.CLASS_DEFINITION,
        answers=[
            StringMatchAnswer(
                answer="class Session(BaseModel):",
                line_number=42,
                answer_template="StringMatchAnswer",
                fully_qualified_class_name=["google.adk.sessions.session"],
            )
        ],
    )


@pytest.mark.asyncio
async def test_ground_truth_answer_generator(mock_api_case: ApiUnderstandingBenchmarkCase):
    """Tests that the GroundTruthAnswerGenerator returns the correct answer."""
    generator = GroundTruthAnswerGenerator()
    generated_answer = await generator.generate_answer(mock_api_case)
    assert generated_answer.output.code == "class Session(BaseModel):"
    assert (
        generated_answer.output.fully_qualified_class_name == "google.adk.sessions.session"
    )


@pytest.mark.asyncio
async def test_trivial_answer_generator(mock_api_case: ApiUnderstandingBenchmarkCase):
    """Tests that the TrivialAnswerGenerator returns a trivial answer."""
    generator = TrivialAnswerGenerator()
    generated_answer = await generator.generate_answer(mock_api_case)
    assert generated_answer.output.code == "class Trivial:"
    assert generated_answer.output.fully_qualified_class_name == "trivial.module"


@pytest.mark.asyncio
async def test_gemini_answer_generator(mock_api_case: ApiUnderstandingBenchmarkCase):
    """Tests the GeminiAnswerGenerator with a mocked API client."""
    with patch(
        "benchmarks.answer_generators.gemini_answer_generator.genai.Client"
    ) as mock_client:
        mock_response = MagicMock()
        mock_response.text = (
            '{"code": "mocked class", "fully_qualified_class_name": "mocked.module"}'
        )
        # The generator uses client.aio.models.generate_content
        mock_client.return_value.aio.models.generate_content = AsyncMock(
            return_value=mock_response
        )

        generator = GeminiAnswerGenerator()
        generated_answer = await generator.generate_answer(mock_api_case)

        assert generated_answer.output.code == "mocked class"
        assert generated_answer.output.fully_qualified_class_name == "mocked.module"
        mock_client.return_value.aio.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_adk_answer_generator(mock_api_case: ApiUnderstandingBenchmarkCase):
    """Tests the AdkAnswerGenerator with a mocked ADK runner."""
    with patch(
        "benchmarks.answer_generators.adk_answer_generator.InMemoryRunner"
    ) as MockInMemoryRunner:
        mock_runner_instance = MockInMemoryRunner.return_value

        mock_runner_instance.session_service = MagicMock()
        mock_runner_instance.session_service.create_session = AsyncMock()
        mock_runner_instance.session_service.create_session.return_value = MagicMock(id="benchmark_session", user_id="benchmark_user")

        mock_events = [
            Event(
                author="model",
                content=types.Content(
                    parts=[
                        types.Part(
                            text='{"code": "adk class", "fully_qualified_class_name": "adk.module"}'
                        )
                    ]
                ),
            )
        ]

        # Manually create an async generator to ensure __aiter__ behavior
        async def real_async_generator(*args, **kwargs):
            for event in mock_events:
                yield event
        
        call_count = 0
        async def counting_async_generator(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            async for event in real_async_generator(*args, **kwargs):
                yield event
        mock_runner_instance.run_async = counting_async_generator

        generator = AdkAnswerGenerator()
        generated_answer = await generator.generate_answer(mock_api_case)

        assert generated_answer.output.code == "adk class"
        assert generated_answer.output.fully_qualified_class_name == "adk.module"
        assert call_count == 1
        mock_runner_instance.session_service.create_session.assert_called_once()
        MockInMemoryRunner.assert_called_once()
