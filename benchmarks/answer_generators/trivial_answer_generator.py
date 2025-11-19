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

"""An answer generator that returns a trivial (empty) answer."""

from benchmarks.answer_generators.base import AnswerGenerator
from benchmarks.data_models import (
    AnswerTemplate,
    ApiUnderstandingAnswerOutput,
    ApiUnderstandingBenchmarkCase,
    BaseBenchmarkCase,
    FixErrorAnswerOutput,
    GeneratedAnswer,
)


class TrivialAnswerGenerator(AnswerGenerator):
    """An answer generator that returns a trivial (empty) answer."""

    async def generate_answer(self, benchmark_case: BaseBenchmarkCase) -> GeneratedAnswer:
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
            output = ApiUnderstandingAnswerOutput(code=code, module_path="trivial.module")
            return GeneratedAnswer(output=output)
        output = FixErrorAnswerOutput(code="agent = Agent()")
        return GeneratedAnswer(output=output)
