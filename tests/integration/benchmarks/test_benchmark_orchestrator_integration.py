"""Integration tests for the BenchmarkOrchestrator."""
import pytest
from pathlib import Path
import yaml

from google.adk.benchmarks.benchmark_orchestrator import run_benchmarks
from google.adk.benchmarks.answer_generators import TrivialAnswerGenerator
from google.adk.benchmarks.data_models import BenchmarkRunResult


@pytest.mark.asyncio
async def test_run_benchmarks_orchestrator(tmp_path: Path):
  """Verify that the benchmark orchestrator can run a simple suite."""
  # GIVEN: A simple benchmark suite file and a trivial answer generator
  suite_content = {
      "name": "Test Suite",
      "description": "A suite for integration testing.",
      "benchmarks": [
          {
              "name": "Test Case 1",
              "description": "A simple API understanding test case.",
              "type": "api_understanding",
              "api_spec": "some_spec_here",
              "expected_request_body": "What is the capital of France?",
              "question": "What is the capital of France?",
          }
      ],
  }
  suite_file = tmp_path / "test_suite.yaml"
  with open(suite_file, "w", encoding="utf-8") as f:
    yaml.dump(suite_content, f)

  answer_generators = [TrivialAnswerGenerator()]

  # WHEN: The orchestrator runs the benchmarks
  results = await run_benchmarks([str(suite_file)], answer_generators)

  # THEN: The results are correct
  assert isinstance(results, list)
  assert len(results) == 1

  result = results[0]
  assert isinstance(result, BenchmarkRunResult)
  assert result.suite == "test_suite.yaml"
  assert result.benchmark_name == "Test Case 1"
  assert result.answer_generator == "TrivialAnswerGenerator"
  # The TrivialAnswerGenerator's output is the question. The
  # ApiUnderstandingRunner will compare this to expected_request_body. Since they
  # match, it should pass.
  assert result.result == 1
  assert result.answer == "What is the capital of France?"
  assert result.validation_error is None
