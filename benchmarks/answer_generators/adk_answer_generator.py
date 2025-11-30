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
import json
import uuid

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session
from google.genai import types

from benchmarks.answer_generators.base import AnswerGenerator
from benchmarks.data_models import (
    AnswerTemplate,
    ApiUnderstandingAnswerOutput,
    ApiUnderstandingBenchmarkCase,
    BaseBenchmarkCase,
    FixErrorBenchmarkCase,
    MultipleChoiceBenchmarkCase,
    FixErrorAnswerOutput,
    MultipleChoiceAnswerOutput,
    GeneratedAnswer,
)
from benchmarks.validation_utils import TEMPLATES


class AdkAnswerGenerator(AnswerGenerator):
    """An AnswerGenerator that uses an ADK Agent."""

    def __init__(self, agent: Agent, name: str | None = None):
        super().__init__()
        self.agent = agent
        self._name = name or f"AdkAnswerGenerator({self.agent.name})"
        self.runner = InMemoryRunner(agent=self.agent)

    @property
    def name(self) -> str:
        """Returns a unique name for this generator instance."""
        return self._name

    async def generate_answer(
        self, benchmark_case: BaseBenchmarkCase
    ) -> GeneratedAnswer:
        """Generates an answer using the ADK Agent."""
        prompt, output_schema_class = self._create_prompt_and_schema(benchmark_case)

        # Run the agent asynchronously.
        response_text = await self._run_agent_async(prompt)

        # Extract JSON from markdown code block if present
        if "```json" in response_text:
            json_str = response_text.split("```json", 1)[1].split("```", 1)[0].strip()
        else:
            json_str = response_text.strip()
        
        # Parse the JSON response into the appropriate Pydantic model.
        # This will raise a ValidationError if the schema doesn't match.
        output = output_schema_class.model_validate_json(json_str)
        return GeneratedAnswer(output=output)

    async def _run_agent_async(self, prompt: str) -> str:
        """Helper to run the agent and get the response."""
        session_id = f"benchmark_session_{uuid.uuid4()}"
        session = await self.runner.session_service.create_session(
            app_name=self.runner.app_name,
            user_id="benchmark_user",
            session_id=session_id,
        )
        final_response = ""

        new_message = types.UserContent(parts=[types.Part(text=prompt)])

        async for event in self.runner.run_async(
            user_id=session.user_id, session_id=session.id, new_message=new_message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                break
        return final_response

    def _create_prompt_and_schema(
        self, case: BaseBenchmarkCase
    ) -> tuple[str, type[ApiUnderstandingAnswerOutput | FixErrorAnswerOutput | MultipleChoiceAnswerOutput]]:
        """Creates a prompt for the ADK agent and returns the expected output schema class."""
        if isinstance(case, ApiUnderstandingBenchmarkCase):
            template_info = TEMPLATES[case.template]
            examples = "\n".join(f"- {example}" for example in template_info.examples)
            schema_json = json.dumps(
                ApiUnderstandingAnswerOutput.model_json_schema(), indent=2
            )

            example_1_output = {
                "code": "class SequentialAgent(google.adk.agents.agent.Agent):",
                "fully_qualified_class_name": "google.adk.agents.sequential_agent.SequentialAgent",
                "rationale": "The `SequentialAgent` class in `google.adk.agents.sequential_agent` is used to create a sequential agent.",
            }
            example_2_output = {
                "code": "def run(self, request: \"RunnerRequest\") -> \"RunnerResponse\":",
                "fully_qualified_class_name": "google.adk.runners.Runner",
                "rationale": "The `run` method in the `Runner` class is used to execute an agent.",
            }
            example_3_output = {
                "code": "model: str | Llm | None = None,",
                "fully_qualified_class_name": "google.adk.agents.llm_agent.LlmAgent",
                "rationale": "The `model` parameter in the `LlmAgent` class is used to define the LLM.",
            }

            prompt = (
                "Please provide a Python type definition that answers the following "
                "question about the ADK Python API. The definition must conform to "
                "the specified template structure. Return the result as a JSON "
                "object with two keys: 'code' for the resulting definition and "
                "'fully_qualified_class_name' for the fully qualified name of the "
                "*class* where the API element is defined (do not include method or "
                "parameter names in the fully qualified class name). Make sure you include the actual class name in the path.\n"
                f"The JSON output should conform to the following Pydantic schema:\n```json\n{schema_json}\n```\n\n"
                "Here are a few examples:\n\n"
                "Question: What is the main class for creating a sequential agent in the "
                "ADK?\n"
                "Rationale: The user is asking for the primary class to instantiate a "
                "sequential agent.\n"
                f'Template: "{TEMPLATES[AnswerTemplate.CLASS_DEFINITION].description}"\n'
                "Answer: \n"
                f"```json\n{json.dumps(example_1_output, indent=2)}\n```\n\n"
                "Question: Which method is used to execute an agent in the ADK?\n"
                "Rationale: The user wants to know the function to run an agent.\n"
                f'Template: "{TEMPLATES[AnswerTemplate.METHOD_DEFINITION].description}"\n'
                "Answer: \n"
                f"```json\n{json.dumps(example_2_output, indent=2)}\n```\n\n"
                "Question: What parameter defines the LLM to be used in an LlmAgent?\n"
                "Rationale: The user needs to identify the specific parameter for "
                "setting the language model in an LlmAgent.\n"
                f'Template: "{TEMPLATES[AnswerTemplate.PARAMETER_DEFINITION].description}"\n'
                "Answer: \n"
                f"```json\n{json.dumps(example_3_output, indent=2)}\n```\n\n"
                "Now, answer the following question:\n\n"
                f"Question: {case.question}\n"
                f"Rationale: {case.rationale}\n"
                f"Template: {template_info.description}\n"
                f"Examples:\n{examples}\n"
            )
            return prompt, ApiUnderstandingAnswerOutput
        elif isinstance(case, FixErrorBenchmarkCase):
            schema_json = json.dumps(
                FixErrorAnswerOutput.model_json_schema(), indent=2
            )
            requirements_str = "\n".join(
                f"- {req}" for req in (case.requirements or [])
            )
            
            if not case.unfixed_file:
                raise ValueError("unfixed_file not specified in benchmark case.")

            if not case.unfixed_file.exists():
                raise FileNotFoundError(f"Unfixed file not found: {case.unfixed_file}")

            full_unfixed_content = case.unfixed_file.read_text()

            prompt = (
                "Your task is to fix the Python code provided. "
                "You will be given a problem description, requirements for the fix, "
                "and the content of the file where the fix needs to be applied. "
                "Your response should be a JSON object conforming to the following Pydantic schema, "
                "enclosed in a markdown code block (```json...```):\n"
                f"```json\n{schema_json}\n```\n\n"
                f"Problem: {case.description}\n"
                f"Requirements:\n{requirements_str}\n\n"
                f"Code Context (from {case.unfixed_file}):\n"
                "```python\n"
                f"{full_unfixed_content}\n"
                "```\n\n"
                "You must provide the complete, corrected code for the entire file in the `code` field of the JSON output. "
                "CRITICAL: Your output MUST define a function with the exact signature: `def create_agent(model_name: str) -> BaseAgent:` "
                "The code should be a complete and valid Python file and **must include all necessary imports** for the code to function correctly. "
                "DO NOT include any other explanatory text or markdown outside the JSON object."
            )
            return prompt, FixErrorAnswerOutput
        elif isinstance(case, MultipleChoiceBenchmarkCase):
            schema_json = json.dumps(
                MultipleChoiceAnswerOutput.model_json_schema(), indent=2
            )
            options_str = "\n".join(
                f"{key}: {value}" for key, value in case.options.items()
            )
            prompt = (
                "Answer the following multiple-choice question. "
                "Your response should be a JSON object conforming to the following Pydantic schema, "
                "enclosed in a markdown code block (```json...```):\n"
                f"```json\n{schema_json}\n```\n\n"
                f"Question: {case.question}\n"
                f"Options:\n{options_str}\n\n"
                "Please provide the single letter corresponding to the chosen answer (e.g., 'A', 'B', 'C', or 'D')."
            )
            return prompt, MultipleChoiceAnswerOutput
        else:
            raise TypeError(f"Unsupported benchmark case type: {type(case)}")
