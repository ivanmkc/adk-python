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

"""An AnswerGenerator that uses an ADK Agent to generate answers."""

import asyncio

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session

from benchmarks.answer_generators.base import AnswerGenerator
from benchmarks.data_models import (
    ApiUnderstandingBenchmarkCase,
    BaseBenchmarkCase,
    FixErrorBenchmarkCase,
    GeneratedAnswer,
    ApiUnderstandingAnswerOutput,
    AnswerTemplate,
)
from benchmarks.validation_utils import TEMPLATES


class AdkAnswerGenerator(AnswerGenerator):
    """An AnswerGenerator that uses an ADK Agent."""

    def __init__(self, model_name: str = "gemini-2.5-pro"):
        super().__init__()
        self.model_name = model_name
        self.agent = LlmAgent(
            name="adk_test_agent",
            model=self.model_name,
            instruction=(
                "You are a senior engineer specializing in the ADK Python framework. "
                "Your task is to answer questions about the ADK API with expert "
                "precision."
            ),
            output_schema=ApiUnderstandingAnswerOutput,
        )
        self.runner = InMemoryRunner(root_agent=self.agent)

    @property
    def name(self) -> str:
        """Returns a unique name for this generator instance."""
        return f"AdkAnswerGenerator({self.model_name})"

    async def generate_answer(self, benchmark_case: BaseBenchmarkCase) -> GeneratedAnswer:
        """Generates an answer using the ADK Agent."""
        if isinstance(benchmark_case, FixErrorBenchmarkCase):
            # The ADK agent is not designed to handle fix_error cases.
            # This could be extended in the future.
            return GeneratedAnswer(output=None)

        if not isinstance(benchmark_case, ApiUnderstandingBenchmarkCase):
            raise TypeError(
                "ADKAnswerGenerator only supports ApiUnderstandingBenchmarkCase."
            )

        prompt = self._create_prompt(benchmark_case)

        # Run the agent asynchronously.
        response = await self._run_agent_async(prompt)

        # The agent's response should be a JSON string that can be parsed
        # into the ApiUnderstandingAnswerOutput schema.
        output = ApiUnderstandingAnswerOutput.model_validate_json(response)
        return GeneratedAnswer(output=output)

    async def _run_agent_async(self, prompt: str) -> str:
        """Helper to run the agent and get the response."""
        session = await self.runner.create_session()
        final_response = ""
        async for event in self.runner.run(session.id, prompt):
            if event.is_final_response():
                final_response = event.content.parts[0].text
                break
        return final_response

    def _create_prompt(self, case: ApiUnderstandingBenchmarkCase) -> str:
        """Creates a prompt for the ADK agent."""
        template_info = TEMPLATES[case.template]
        examples = "\n".join(f"- {example}" for example in template_info.examples)
        return (
            "Please provide a Python type definition that answers the following "
            "question about the ADK Python API. The definition must conform to "
            "the specified template structure. Return the result as a JSON "
            "object with two keys: 'code' for the resulting definition and "
            "'fully_qualified_class_name' for the fully qualified name of the "
            "*class* where the API element is defined (do not include method or "
            "parameter names in the fully qualified class name). Make sure you include the actual class name in the path."
            "\n\n"
            "Here are a few examples:\n\n"
            "Question: What is the main class for creating a sequential agent in the "
            "ADK?\n"
            "Rationale: The user is asking for the primary class to instantiate a "
            "sequential agent.\n"
            f'Template: "{TEMPLATES[AnswerTemplate.CLASS_DEFINITION].description}"\n'
            "Answer: \n"
            "```json\n"
            "{\n"
            '    "code": "class SequentialAgent(google.adk.agents.agent.Agent):",\n'
            '    "fully_qualified_class_name": "google.adk.agents.sequential_agent.SequentialAgent"\n'
            "}\n"
            "```\n\n"
            "Question: Which method is used to execute an agent in the ADK?\n"
            "Rationale: The user wants to know the function to run an agent.\n"
            f'Template: "{TEMPLATES[AnswerTemplate.METHOD_DEFINITION].description}"\n'
            "Answer: \n"
            "```json\n"
            "{\n"
            '    "code": "def run(self, request: "RunnerRequest") -> "RunnerResponse":",\n'
            '    "fully_qualified_class_name": "google.adk.runners.Runner"\n'
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
            '    "fully_qualified_class_name": "google.adk.agents.llm_agent.LlmAgent"\n'
            "}\n"
            "```\n\n"
            "Now, answer the following question:\n\n"
            f"Question: {case.question}\n"
            f"Rationale: {case.rationale}\n"
            f"Template: {template_info.description}\n"
            f"Examples:\n{examples}\n"
        )
