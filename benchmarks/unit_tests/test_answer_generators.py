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
                module_path="google.adk.sessions.session",
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
        generated_answer.output.module_path == "google.adk.sessions.session"
    )


@pytest.mark.asyncio
async def test_trivial_answer_generator(mock_api_case: ApiUnderstandingBenchmarkCase):
    """Tests that the TrivialAnswerGenerator returns a trivial answer."""
    generator = TrivialAnswerGenerator()
    generated_answer = await generator.generate_answer(mock_api_case)
    assert generated_answer.output.code == "class Trivial:"
    assert generated_answer.output.module_path == "trivial.module"


@pytest.mark.asyncio
async def test_gemini_answer_generator(mock_api_case: ApiUnderstandingBenchmarkCase):
    """Tests the GeminiAnswerGenerator with a mocked API client."""
    with patch(
        "benchmarks.answer_generators.gemini_answer_generator.genai.Client"
    ) as mock_client:
        mock_response = MagicMock()
        mock_response.text = (
            '{"code": "mocked class", "module_path": "mocked.module"}'
        )
        mock_client.return_value.models.generate_content = AsyncMock(
            return_value=mock_response
        )

        generator = GeminiAnswerGenerator()
        generated_answer = await generator.generate_answer(mock_api_case)

        assert generated_answer.output.code == "mocked class"
        assert generated_answer.output.module_path == "mocked.module"
        mock_client.return_value.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_adk_answer_generator(mock_api_case: ApiUnderstandingBenchmarkCase):
    """Tests the AdkAnswerGenerator with a mocked ADK runner."""
    with patch(
        "benchmarks.answer_generators.adk_answer_generator.InMemoryRunner"
    ) as mock_runner:
        mock_runner.return_value.create_session = AsyncMock()
        mock_runner.return_value.run = MagicMock()
        mock_runner.return_value.run.return_value.__aiter__.return_value = [
            MagicMock(
                is_final_response=lambda: True,
                content=MagicMock(
                    parts=[
                        MagicMock(
                            text='{"code": "adk class", "module_path": "adk.module"}'
                        )
                    ]
                ),
            )
        ]

        generator = AdkAnswerGenerator()
        generated_answer = await generator.generate_answer(mock_api_case)

        assert generated_answer.output.code == "adk class"
        assert generated_answer.output.module_path == "adk.module"
        mock_runner.return_value.run.assert_called_once()
