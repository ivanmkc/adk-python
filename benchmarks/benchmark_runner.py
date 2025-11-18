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
from typing import Generic, TypeVar, Optional

import pytest

from benchmarks.data_models import (
    ApiUnderstandingBenchmarkCase,
    BaseBenchmarkCase,
    FixErrorBenchmarkCase,
    GeneratedAnswer,
)
from benchmarks.validation_utils import (
    ValidationError,
    validate_answer_against_template,
    validate_module_path,
)

# A TypeVar to create a generic link between a runner and the case it handles.
BenchmarkCaseT = TypeVar("BenchmarkCaseT", bound=BaseBenchmarkCase)


class BenchmarkRunner(abc.ABC, Generic[BenchmarkCaseT]):
    """Abstract base class for benchmark runners."""

    @abc.abstractmethod
    async def run_benchmark(
        self, benchmark_case: BenchmarkCaseT, generated_answer: GeneratedAnswer
    ) -> tuple[str, Optional[str], Optional[str]]:
        """Runs a benchmark and returns the result."""
        pass


class PytestBenchmarkRunner(BenchmarkRunner[FixErrorBenchmarkCase]):
    """A benchmark runner that uses pytest to run the tests."""

    async def run_benchmark(
        self, benchmark_case: FixErrorBenchmarkCase, generated_answer: GeneratedAnswer
    ) -> tuple[str, str, str]:
        """Runs a benchmark using pytest and returns the result and logs."""
        code_to_test = generated_answer.output.code
        project_root = Path(__file__).parent.parent
        test_file_path = project_root / benchmark_case.test_file

        if not test_file_path.exists():
            raise FileNotFoundError(f"Could not find test file: {test_file_path}")

        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Replace the code block with the code to test.
        new_content = content.replace(
            "# BEGIN: CODE\n# END: CODE", f"# BEGIN: CODE\n{code_to_test}\n# END: CODE"
        )

        tmpdir = tempfile.mkdtemp(prefix="benchmark_")
        tmp_path = Path(tmpdir) / "test_temp.py"
        with open(tmp_path, "w", encoding="utf-8") as tmp:
            tmp.write(new_content)

        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "pytest",
            str(tmp_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        logs = (
            f"--- Pytest stdout ---\n{stdout.decode()}\n"
            f"--- Pytest stderr ---\n{stderr.decode()}"
        )
        result = "pass" if proc.returncode == 0 else "fail"
        return result, logs, str(tmp_path)


import re


class ApiUnderstandingRunner(BenchmarkRunner[ApiUnderstandingBenchmarkCase]):
    """
    A benchmark runner that validates answers for API understanding.
    """

    def _normalize_code(self, code: str) -> str:
        """Removes all whitespace from a code string for comparison."""
        return re.sub(r"\s+", "", code)

    async def run_benchmark(
        self,
        benchmark_case: ApiUnderstandingBenchmarkCase,
        generated_answer: GeneratedAnswer,
    ) -> tuple[str, str, None]:
        """Validates the generated answer and returns the result and logs."""
        all_errors = []
        output = generated_answer.output
        code_to_test = output.code
        module_path_to_test = output.module_path

        for ground_truth in benchmark_case.answers:
            try:
                validate_answer_against_template(code_to_test, benchmark_case.template)
                normalized_code = self._normalize_code(code_to_test)
                normalized_ground_truth = self._normalize_code(ground_truth.answer)
                if normalized_code != normalized_ground_truth:
                    raise ValidationError(
                        "Normalized code does not match normalized ground truth."
                    )
                validate_module_path(module_path_to_test, benchmark_case.file)
                return "pass", "Validation successful.", None

            except ValidationError as e:
                all_errors.append(
                    f"  - Ground Truth '{self._normalize_code(ground_truth.answer)}'"
                    f" failed: {e}"
                )

        logs = (
            f"--- Validation Failed for: {benchmark_case.get_identifier()} ---\n"
            + "\n".join(all_errors)
        )
        return "fail", logs, None
