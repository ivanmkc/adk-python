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

"""An answer generator that returns the ground truth answer."""

import re
from pathlib import Path

from benchmarks.answer_generators.base import AnswerGenerator
from benchmarks.data_models import (
    ApiUnderstandingAnswerOutput,
    ApiUnderstandingBenchmarkCase,
    BaseBenchmarkCase,
    FixErrorAnswerOutput,
    FixErrorBenchmarkCase,
    GeneratedAnswer,
)


class GroundTruthAnswerGenerator(AnswerGenerator):
    """An answer generator that returns the ground truth answer."""

    @property
    def name(self) -> str:
        """Returns the name of the generator."""
        return "GroundTruthAnswerGenerator"

    def _get_ground_truth_file_map(self) -> dict[str, Path]:
        """Maps fix_error test file names to their ground truth counterparts."""
        ground_truth_base_path = Path("benchmarks/test_data/ground_truth")
        return {f.name: f for f in ground_truth_base_path.glob("test_*.py")}

    def _extract_code_snippet(self, file_path: Path) -> str:
        """Extracts the code snippet from a file."""
        with open(file_path, "r") as f:
            content = f.read()
        match = re.search(r"# BEGIN: CODE\n(.*?)# END: CODE", content, re.DOTALL)
        if not match:
            raise ValueError(f"Could not find code snippet in {file_path}")
        return match.group(1).strip()

    async def generate_answer(self, benchmark_case: BaseBenchmarkCase) -> GeneratedAnswer:
        """Returns the ground truth answer for the benchmark case."""
        if isinstance(benchmark_case, FixErrorBenchmarkCase):
            code = self._extract_code_snippet(benchmark_case.test_file)
            output = FixErrorAnswerOutput(code=code)
            return GeneratedAnswer(output=output)
        elif isinstance(benchmark_case, ApiUnderstandingBenchmarkCase):
            answer = benchmark_case.answers[0]
            output = ApiUnderstandingAnswerOutput(
                code=answer.answer, module_path=answer.module_path
            )
            return GeneratedAnswer(output=output)
        else:
            raise TypeError(f"Unknown benchmark case type: {type(benchmark_case)}")
