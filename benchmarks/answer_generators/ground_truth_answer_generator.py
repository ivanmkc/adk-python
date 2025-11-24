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

from pathlib import Path
import re
import textwrap

from benchmarks.answer_generators.base import AnswerGenerator
from benchmarks.data_models import ApiUnderstandingAnswerOutput
from benchmarks.data_models import ApiUnderstandingBenchmarkCase
from benchmarks.data_models import BaseBenchmarkCase
from benchmarks.data_models import FixErrorAnswerOutput
from benchmarks.data_models import FixErrorBenchmarkCase
from benchmarks.data_models import GeneratedAnswer
from benchmarks.data_models import MultipleChoiceAnswerOutput
from benchmarks.data_models import MultipleChoiceBenchmarkCase


class GroundTruthAnswerGenerator(AnswerGenerator):
    """An answer generator that returns the ground truth answer."""

    @property
    def name(self) -> str:
        """Returns the name of the generator."""
        return "GroundTruthAnswerGenerator"

    def _get_ground_truth_file_map(self) -> dict[str, Path]:
        """Maps fix_error test file names to their ground truth counterparts."""
        ground_truth_base_path = Path("benchmarks/ground_truth/fix_errors")
        return {f.name: f for f in ground_truth_base_path.glob("test_*.py")}

    def _extract_code_snippet(self, file_path: Path) -> str:
        """Extracts the code snippet from a file."""
        import textwrap

        with open(file_path, "r") as f:
            content = f.read()
        match = re.search(r"# BEGIN: CODE.*?\s*\n(.*?)\s*# END: CODE", content, re.DOTALL)
        if not match:
            raise ValueError(f"Could not find code snippet in {file_path}")
        # Dedent the extracted code to ensure it's at a consistent base level
        return textwrap.dedent(match.group(1))

    async def generate_answer(
        self, benchmark_case: BaseBenchmarkCase
    ) -> GeneratedAnswer:
        """Returns the ground truth answer for the benchmark case."""
        if isinstance(benchmark_case, FixErrorBenchmarkCase):
            # The benchmark case points to the test file template (which has empty code blocks).
            # We need to read the *ground truth* file which has the filled-in code.
            ground_truth_map = self._get_ground_truth_file_map()
            test_filename = benchmark_case.test_file.name

            if test_filename not in ground_truth_map:
                # Fallback: try to find it directly if map fails or is incomplete
                ground_truth_path = (
                    Path("benchmarks/ground_truth/fix_errors") / test_filename
                )
            else:
                ground_truth_path = ground_truth_map[test_filename]

            if not ground_truth_path.exists():
                raise FileNotFoundError(
                    f"Ground truth file not found for {test_filename} at {ground_truth_path}"
                )

            code = self._extract_code_snippet(ground_truth_path)
            output = FixErrorAnswerOutput(code=code, rationale="Ground truth answer.")
            return GeneratedAnswer(output=output)
        elif isinstance(benchmark_case, ApiUnderstandingBenchmarkCase):
            answer = benchmark_case.answers[0]
            output = ApiUnderstandingAnswerOutput(
                code=answer.answer,
                fully_qualified_class_name=answer.fully_qualified_class_name[0],
                rationale="Ground truth answer.",
            )
            return GeneratedAnswer(output=output)
        elif isinstance(benchmark_case, MultipleChoiceBenchmarkCase):
            output = MultipleChoiceAnswerOutput(
                answer=benchmark_case.correct_answer, rationale="Ground truth answer."
            )
            return GeneratedAnswer(output=output)
        else:
            raise TypeError(f"Unknown benchmark case type: {type(benchmark_case)}")
