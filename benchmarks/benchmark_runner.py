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
from pathlib import Path
import sys
import tempfile
from typing import Generic
from typing import Optional
from typing import TypeVar

import pytest

from benchmarks.data_models import ApiUnderstandingBenchmarkCase
from benchmarks.data_models import BaseBenchmarkCase
from benchmarks.data_models import FixErrorBenchmarkCase
from benchmarks.data_models import GeneratedAnswer
from benchmarks.data_models import MultipleChoiceBenchmarkCase
import benchmarks.validation_utils as validation_utils

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


class MultipleChoiceRunner(BenchmarkRunner[MultipleChoiceBenchmarkCase]):
    """Runs a multiple choice benchmark."""

    async def run_benchmark(
        self,
        benchmark_case: MultipleChoiceBenchmarkCase,
        generated_answer: GeneratedAnswer,
    ) -> tuple[str, Optional[str], Optional[str]]:
        """Checks if the answer matches the correct option."""
        answer = generated_answer.output.answer.strip().upper()
        correct = benchmark_case.correct_answer.strip().upper()

        if answer == correct:
            return "pass", None, None
        else:
            return (
                "fail",
                f"Expected '{correct}', but got '{answer}'.\nQuestion: {benchmark_case.question}",
                None,
            )


class PytestBenchmarkRunner(BenchmarkRunner[FixErrorBenchmarkCase]):
    """A benchmark runner that uses pytest to run the tests."""

    def _inject_code(self, content: str, code: str) -> str:
        """Injects code between markers, respecting indentation."""
        import textwrap

        lines = content.splitlines()
        new_lines = []
        in_block = False

        for line in lines:
            if "# BEGIN: CODE" in line:
                new_lines.append(line)
                in_block = True

                # Determine indentation from the marker line
                indent = line[: line.find("# BEGIN: CODE")]

                # Indent the code to match
                if code:
                    dedented_code = textwrap.dedent(code)
                    indented_code = textwrap.indent(dedented_code, indent)
                    new_lines.append(indented_code)

            elif "# END: CODE" in line:
                in_block = False
                new_lines.append(line)
            elif not in_block:
                new_lines.append(line)

        return "\n".join(new_lines)

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

        # Replace the code block with the code to test using robust injection
        new_content = self._inject_code(content, code_to_test)

        tmpdir = tempfile.mkdtemp(prefix="benchmark_")
        tmp_path = Path(tmpdir) / "test_temp.py"
        with open(tmp_path, "w", encoding="utf-8") as tmp:
            tmp.write(new_content)

        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "pytest",
            "--asyncio-mode=auto",
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
        """Normalizes code for comparison by collapsing whitespace to one space and stripping."""
        # Replace all whitespace sequences with a single space
        code = re.sub(r"\s+", " ", code)
        # Remove leading/trailing whitespace
        return code.strip()

    async def run_benchmark(
        self,
        benchmark_case: ApiUnderstandingBenchmarkCase,
        generated_answer: GeneratedAnswer,
    ) -> tuple[str, str, None]:
        """Validates the generated answer and returns the result and logs."""
        all_errors = []
        output = generated_answer.output
        code_to_test = output.code

        for ground_truth in benchmark_case.answers:
            try:
                validation_utils.validate_answer_against_template(
                    code_to_test, benchmark_case.template
                )
                normalized_code = self._normalize_code(code_to_test)
                normalized_ground_truth = self._normalize_code(ground_truth.answer)
                if normalized_ground_truth not in normalized_code:
                    raise validation_utils.ValidationError(
                        "Normalized code does not match normalized ground truth."
                    )
                validation_utils.validate_module_path(
                    fully_qualified_class_name=generated_answer.output.fully_qualified_class_name,
                    expected_paths=ground_truth.fully_qualified_class_name,
                )
                return "pass", "Validation successful.", None

            except validation_utils.ValidationError as e:
                all_errors.append(
                    f"  - Ground Truth '{self._normalize_code(ground_truth.answer)}'"
                    f" failed: {e}"
                )

        logs = (
            f"--- Validation Failed for: {benchmark_case.get_identifier()} ---\n"
            + "\n".join(all_errors)
        )
        return "fail", logs, None
