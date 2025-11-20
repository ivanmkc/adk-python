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

from __future__ import annotations

import os
import sys

import pytest

# Add the project root to the path to allow absolute imports from 'benchmarks'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from benchmarks.answer_generators.adk_answer_generator import AdkAnswerGenerator
from benchmarks.answer_generators.gemini_answer_generator import GeminiAnswerGenerator
from benchmarks.answer_generators.ground_truth_answer_generator import (
    GroundTruthAnswerGenerator,
)
from benchmarks.answer_generators.trivial_answer_generator import (
    TrivialAnswerGenerator,
)
from benchmarks.data_models import BenchmarkCase, GeneratedAnswer


@pytest.fixture
def sample_benchmark_case() -> BenchmarkCase:
  """Provides a sample BenchmarkCase for integration testing."""
  return BenchmarkCase(
      benchmark_type="api_understanding",
      question="What is the foundational class for all agents in the ADK?",
      answers=[
          {
              "answer_template": "StringMatchAnswer",
              "answer": "class BaseAgent(BaseModel):",
              "module_path": "google.adk.agents.base_agent",
          }
      ],
      category="Core Class Signatures & Initialization",
      template="CLASS_DEFINITION",
      rationale="All agents must inherit from `google.adk.agents.base_agent.BaseAgent`",
      file="src/google/adk/agents/base_agent.py",
  )


@pytest.mark.asyncio
async def test_ground_truth_answer_generator_integration(
    sample_benchmark_case: BenchmarkCase,
):
  """Tests that the GroundTruthAnswerGenerator returns the ground truth."""
  generator = GroundTruthAnswerGenerator()
  answer = await generator.generate_answer(sample_benchmark_case)
  assert isinstance(answer, GeneratedAnswer)
  assert answer.output.code == "class BaseAgent(BaseModel):"


@pytest.mark.asyncio
async def test_trivial_answer_generator_integration(
    sample_benchmark_case: BenchmarkCase,
):
  """Tests that the TrivialAnswerGenerator returns the module path."""
  generator = TrivialAnswerGenerator()
  answer = await generator.generate_answer(sample_benchmark_case)
  assert isinstance(answer, GeneratedAnswer)
  assert answer.output.module_path == "google.adk.agents.base_agent"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_gemini_answer_generator_integration(
    sample_benchmark_case: BenchmarkCase,
):
  """Tests the GeminiAnswerGenerator against the live Gemini API."""
  generator = GeminiAnswerGenerator()
  answer = await generator.generate_answer(sample_benchmark_case)
  assert isinstance(answer, GeneratedAnswer)
  assert answer.output.code.strip()  # Assert that the answer is not empty
  assert "BaseAgent" in answer.output.code


@pytest.mark.asyncio
@pytest.mark.integration
async def test_adk_answer_generator_integration(sample_benchmark_case: BenchmarkCase):
  """Tests the AdkAnswerGenerator using a real ADK agent and LLM."""
  generator = AdkAnswerGenerator()
  answer = await generator.generate_answer(sample_benchmark_case)
  assert isinstance(answer, GeneratedAnswer)
  assert answer.output.code.strip()  # Assert that the answer is not empty
  assert "BaseAgent" in answer.output.code

