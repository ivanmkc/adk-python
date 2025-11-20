"""Integration tests for BenchmarkRunners."""
import pytest
from pathlib import Path
from types import SimpleNamespace

from google.adk.benchmarks.benchmark_runner import (
    PytestBenchmarkRunner,
    ApiUnderstandingRunner,
)
from google.adk.benchmarks.data_models import (
    FixErrorBenchmarkCase,
    GeneratedAnswer,
    ApiUnderstandingBenchmarkCase,
    GroundTruth,
)


@pytest.mark.asyncio
async def test_pytest_benchmark_runner_pass_and_fail(tmp_path: Path):
  """Verify PytestBenchmarkRunner correctly runs pytest and gets pass/fail."""
  # GIVEN a template test file that expects a function `function_to_fix`.
  template_content = """
def function_to_fix():
  # BEGIN: CODE
  # END: CODE

def test_fixed_function():
  assert function_to_fix() == 42
"""
  template_file = tmp_path / "test_template.py"
  template_file.write_text(template_content)

  benchmark_case = FixErrorBenchmarkCase(
      name="TestFix",
      description="Test",
      type="fix_error",
      test_file=str(template_file),
      answers=[],
  )
  runner = PytestBenchmarkRunner()

  # WHEN running with code that should pass
  passing_answer = GeneratedAnswer(
      output=SimpleNamespace(code="  return 42", module_path=None)
  )
  pass_result, _, _ = await runner.run_benchmark(benchmark_case, passing_answer)

  # THEN the result is "pass"
  assert pass_result == "pass"

  # WHEN running with code that should fail
  failing_answer = GeneratedAnswer(
      output=SimpleNamespace(code="  return 99", module_path=None)
  )
  fail_result, _, _ = await runner.run_benchmark(benchmark_case, failing_answer)

  # THEN the result is "fail"
  assert fail_result == "fail"


@pytest.mark.asyncio
async def test_api_understanding_runner():
  """Verify ApiUnderstandingRunner correctly validates answers."""
  # GIVEN a benchmark case with a ground truth answer.
  benchmark_case = ApiUnderstandingBenchmarkCase(
      name="TestApi",
      description="Test",
      type="api_understanding",
      api_spec="",
      template="",
      file="my_module/my_file.py",
      answers=[GroundTruth(answer="  print('hello')  ")],
  )
  runner = ApiUnderstandingRunner()

  # WHEN the generated answer is correct
  correct_answer = GeneratedAnswer(
      output=SimpleNamespace(
          code="print('hello')", module_path="my_module/my_file.py"
      )
  )
  pass_result, _, _ = await runner.run_benchmark(benchmark_case, correct_answer)

  # THEN the result is "pass" (due to normalization)
  assert pass_result == "pass"

  # WHEN the generated answer is incorrect
  incorrect_answer = GeneratedAnswer(
      output=SimpleNamespace(
          code="print('world')", module_path="my_module/my_file.py"
      )
  )
  fail_result, _, _ = await runner.run_benchmark(
      benchmark_case, incorrect_answer
  )

  # THEN the result is "fail"
  assert fail_result == "fail"
