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

"""Abstract base classes for benchmark runners."""

import abc
import asyncio
import sys
import tempfile
from pathlib import Path
from typing import Union

import pytest

from benchmarks.data_models import (
    ApiUnderstandingBenchmarkCase,
    BaseBenchmarkCase,
    BenchmarkResult,
    ExpectedOutcome,
    FixErrorBenchmarkCase,
)
from benchmarks.validation_utils import ValidationError, validate_answer_against_template


class BenchmarkRunner(abc.ABC):
  """Abstract base class for benchmark runners."""

  @abc.abstractmethod
  async def run_benchmark(
      self, benchmark_case: BaseBenchmarkCase, code_to_test: str
  ) -> str:
    """Runs a benchmark and returns the result."""
    pass


class PytestBenchmarkRunner(BenchmarkRunner):
  """A benchmark runner that uses pytest to run the tests."""

  async def run_benchmark(
      self, benchmark_case: FixErrorBenchmarkCase, code_to_test: str
  ) -> str:
    """Runs a benchmark using pytest on a temporary file."""
    with open(benchmark_case.test_file, "r", encoding="utf-8") as f:
      content = f.read()

    # Replace the code block with the code to test.
    new_content = content.replace(
        "# BEGIN: CODE\n# END: CODE", f"# BEGIN: CODE\n{code_to_test}\n# END: CODE"
    )

    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        suffix=".py",
        dir=benchmark_case.test_file.parent,
    ) as tmp:
      tmp.write(new_content)
      tmp_path = Path(tmp.name)

    print(f"--- Running pytest for: {benchmark_case.get_identifier()} ---")
    print(f"--- Temporary file: {tmp_path} ---")
    print("--- Code to test ---")
    print(code_to_test)

    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "pytest",
        str(tmp_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    print("--- Pytest stdout ---")
    print(stdout.decode())
    print("--- End Pytest stdout ---")
    print("--- Pytest stderr ---")
    print(stderr.decode())
    print("--- End Pytest stderr ---")

    tmp_path.unlink()

    return "pass" if proc.returncode == 0 else "fail"


class ApiUnderstandingRunner(BenchmarkRunner):
  """A benchmark runner that validates generated answers against templates."""

  async def run_benchmark(
      self, benchmark_case: ApiUnderstandingBenchmarkCase, code_to_test: str
  ) -> str:
    """Validates the generated answer against the template."""
    try:
      validate_answer_against_template(code_to_test, benchmark_case.template)
      return "pass"
    except ValidationError:
      return "fail"
