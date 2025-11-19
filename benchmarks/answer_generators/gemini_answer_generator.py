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

"""An AnswerGenerator that uses the Gemini API to generate answers."""

from google import genai

from benchmarks.answer_generators.base import AnswerGenerator
from benchmarks.validation_utils import TEMPLATES
from benchmarks.data_models import (
    ApiUnderstandingBenchmarkCase,
    BaseBenchmarkCase,
    FixErrorBenchmarkCase,
    GeneratedAnswer,
    FixErrorAnswerOutput,
    ApiUnderstandingAnswerOutput,
    AnswerTemplate,
)



class GeminiAnswerGenerator(AnswerGenerator):
    """An AnswerGenerator that uses the Gemini API."""

    def __init__(self, model_name: str = "gemini-2.5-pro"):
        super().__init__()
        self.model_name = model_name
        # api_key = os.environ.get("GEMINI_API_KEY")
        # if not api_key:
        #     raise ValueError("GEMINI_API_KEY environment variable not set.")
        # genai.configure(api_key=api_key)
        self.client = genai.Client()

    def generate_answer(self, benchmark_case: BaseBenchmarkCase) -> GeneratedAnswer:
        """Generates an answer using the Gemini API's structured output feature."""
        if isinstance(benchmark_case, FixErrorBenchmarkCase):
            prompt = self._create_prompt_for_fix_error(benchmark_case)
            response_schema = FixErrorAnswerOutput
        elif isinstance(benchmark_case, ApiUnderstandingBenchmarkCase):
            prompt = self._create_prompt_for_api_understanding(benchmark_case)
            response_schema = ApiUnderstandingAnswerOutput
        else:
            raise TypeError(f"Unsupported benchmark case type: {type(benchmark_case)}")

        json_schema = response_schema.model_json_schema()
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt, 
            config={
                "response_mime_type": "application/json",
                "response_json_schema": json_schema,
            },
        )
        output = response_schema.model_validate_json(response.text)

        return GeneratedAnswer(output=output)

    def _create_prompt_for_fix_error(self, case: FixErrorBenchmarkCase) -> str:
        """Creates a prompt for a fix_error benchmark case."""
        return (
            "Please fix the following Python code snippet. "
            "Return the result as a JSON object with a single key 'code' "
            "containing the corrected code.\n\n"
            f"Description of the error: {case.description}\n\n"
            "Code with error:\n"
            "```python\n"
            f"{self._read_code_from_file(case.test_file, case.start_line, case.end_line)}\n"
            "```"
        )

    def _create_prompt_for_api_understanding(
        self, case: ApiUnderstandingBenchmarkCase
    ) -> str:
        """Creates a prompt for an api_understanding benchmark case."""
        template_info = TEMPLATES[case.template]
        examples = "\n".join(f"- {example}" for example in template_info.examples)
        return (
            "Please provide a Python type definition that answers the following "
            "question about the ADK Python API. The definition must conform to "
            "the specified template structure. Return the result as a JSON "
            "object with two keys: 'code' for the resulting definition and "
            "'module_path' for the module path."
            "\n\n"
            "Here are a few examples:\n\n"
            "Question: What is the main class for creating a sequential agent "
            "in the ADK?\n"
            "Rationale: The user is asking for the primary class to instantiate "
            "a sequential agent.\n"
            f'Template: "{TEMPLATES[AnswerTemplate.CLASS_DEFINITION].description}"\n'
            "Answer: \n"
            "```json\n"
            "{\n"
            '    "code": "class SequentialAgent(google.adk.agents.agent.Agent):",\n'
            '    "module_path": "google.adk.agents.agent.Agent"\n'
            "}\n"
            "```\n\n"
            "Question: Which method is used to execute an agent in the ADK?\n"
            "Rationale: The user wants to know the function to run an agent.\n"
            f'Template: "{TEMPLATES[AnswerTemplate.METHOD_DEFINITION].description}"\n'
            "Answer: \n"
            "```json\n"
            "{\n"
            '    "code": "def run(self, request: "RunnerRequest") -> "RunnerResponse":",\n'
            '    "module_path": "google.adk.runners.Runner"\n'
            "}\n"
            "```\n\n"
            "Question: What parameter defines the LLM to be used in an LlmAgent?\n"
            "Rationale: The user needs to identify the specific parameter for "
            "setting the language model in an LlmAgent.\n"
            f'Template: "{TEMPLATES[AnswerTemplate.PARAMETER_DEFINITION].description}"\n'
            "Answer: \n"
            "```json\n"
            "{\n"
            '    "code": "model: str | Llm | None = None,",\n'
            '    "module_path": "google.adk.agents.llm_agent.LlmAgent"\n'
            "}\n"
            "```\n\n"
            "Now, answer the following question:\n\n"
            f"Question: {case.question}\n"
            f"Rationale: {case.rationale}\n"
            f"Template: {template_info.description}\n"
            f"Examples:\n{examples}\n"
        )

    def _read_code_from_file(self, file_path, start_line, end_line) -> str:
        """Reads a specific range of lines from a file."""
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(lines[start_line - 1 : end_line])
