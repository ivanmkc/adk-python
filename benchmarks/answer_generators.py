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

"""Answer generators for benchmarks."""

import abc
import re
from pathlib import Path

from benchmarks.data_models import (
    AnswerTemplate,
    ApiUnderstandingAnswerOutput,
    ApiUnderstandingBenchmarkCase,
    BaseBenchmarkCase,
    FixErrorAnswerOutput,
    FixErrorBenchmarkCase,
    GeneratedAnswer,
)


class AnswerGenerator(abc.ABC):
  """Abstract base class for answer generators."""

  @abc.abstractmethod
  def generate_answer(self, benchmark_case: BaseBenchmarkCase) -> GeneratedAnswer:
    """Generates an answer for a given benchmark case."""
    pass


class GroundTruthAnswerGenerator(AnswerGenerator):
  """An answer generator that returns the ground truth answer."""

  def _get_ground_truth_file_map(self) -> dict[Path, Path]:
    """Returns a map from fix_error test files to their ground truth counterparts."""
    base_path = Path("benchmarks/test_data/ground_truth")
    ground_truth_base_path = Path("benchmarks/test_data/ground_truth")
    return {
        base_path / f.name: ground_truth_base_path / f.name
        for f in ground_truth_base_path.glob("test_*.py")
    }

  def _extract_code_snippet(self, file_path: Path) -> str:
    """Extracts the code snippet from a file."""
    with open(file_path, "r") as f:
      content = f.read()
    match = re.search(
        r"# BEGIN: CODE\n(.*?)# END: CODE", content, re.DOTALL
    )
    if not match:
      raise ValueError(f"Could not find code snippet in {file_path}")
    return match.group(1).strip()

  def generate_answer(self, benchmark_case: BaseBenchmarkCase) -> GeneratedAnswer:
    """Returns the ground truth answer for the benchmark case."""
    if isinstance(benchmark_case, FixErrorBenchmarkCase):
      file_map = self._get_ground_truth_file_map()
      ground_truth_file = file_map.get(benchmark_case.test_file)
      if not ground_truth_file:
        raise ValueError(
            f"No ground truth file found for {benchmark_case.test_file}"
        )
      code = self._extract_code_snippet(ground_truth_file)
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


class TrivialAnswerGenerator(AnswerGenerator):
  """An answer generator that returns a trivial (empty) answer."""

  def generate_answer(self, benchmark_case: BaseBenchmarkCase) -> GeneratedAnswer:
    """Returns an empty answer for any benchmark case."""
    if isinstance(benchmark_case, ApiUnderstandingBenchmarkCase):
      template_map = {
          AnswerTemplate.CLASS_DEFINITION: "class Trivial:",
          AnswerTemplate.METHOD_DEFINITION: "def trivial():",
          AnswerTemplate.PARAMETER_DEFINITION: "trivial: None",
          AnswerTemplate.TYPE_ALIAS_DEFINITION: "Trivial: TypeAlias = None",
          AnswerTemplate.CODE_BLOCK: "pass",
      }
      code = template_map.get(benchmark_case.template, "")
      output = ApiUnderstandingAnswerOutput(code=code, module_path="")
      return GeneratedAnswer(output=output)
    output = FixErrorAnswerOutput(code="")
    return GeneratedAnswer(output=output)
