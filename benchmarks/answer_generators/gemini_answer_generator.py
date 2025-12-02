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

import hashlib
from pathlib import Path

from benchmarks.answer_generators.base import AnswerGenerator
from benchmarks.data_models import AnswerTemplate
from benchmarks.data_models import ApiUnderstandingAnswerOutput
from benchmarks.data_models import ApiUnderstandingBenchmarkCase
from benchmarks.data_models import BaseBenchmarkCase
from benchmarks.data_models import FixErrorAnswerOutput
from benchmarks.data_models import FixErrorBenchmarkCase
from benchmarks.data_models import GeneratedAnswer
from benchmarks.data_models import MultipleChoiceAnswerOutput
from benchmarks.data_models import MultipleChoiceBenchmarkCase
from benchmarks.data_models import TraceLogEvent
from benchmarks.data_models import UsageMetadata
from benchmarks.validation_utils import load_snippet
from benchmarks.validation_utils import TEMPLATES
from google import genai


class GeminiAnswerGenerator(AnswerGenerator):
  """An AnswerGenerator that uses the Gemini API."""

  def __init__(
      self,
      model_name: str = "gemini-3-pro-preview",
      context: str | Path | None = None,
  ):
    super().__init__()
    self.model_name = model_name
    self.context = context
    self.client = genai.Client().aio

  @property
  def name(self) -> str:
    """Returns a unique name for this generator instance."""
    base_name = f"GeminiAnswerGenerator({self.model_name})"
    if self.context:
      if isinstance(self.context, Path):
        # Use the file name if context is a Path
        return f"{base_name}-with-context-{self.context.name}"
      elif isinstance(self.context, str):
        # For string context, always use a stable hash
        context_id = self.context.strip()
        if context_id:
          context_hash_digest = hashlib.md5(
              context_id.encode("utf-8")
          ).hexdigest()[:8]
          return f"{base_name}-with-context-hash-{context_hash_digest}"
    return base_name

  def _get_context_content(self) -> str:
    """Retrieves the context content, reading from file if necessary."""
    if not self.context:
      return ""
    if isinstance(self.context, Path):
      if not self.context.exists():
        raise FileNotFoundError(f"Context file not found: {self.context}")
      with open(self.context, "r", encoding="utf-8") as f:
        return f.read()
    return self.context

  async def generate_answer(
      self, benchmark_case: BaseBenchmarkCase
  ) -> GeneratedAnswer:
    """Generates an answer using the Gemini API's structured output feature."""
    if isinstance(benchmark_case, FixErrorBenchmarkCase):
      prompt = self._create_prompt_for_fix_error(benchmark_case)
      response_schema = FixErrorAnswerOutput
    elif isinstance(benchmark_case, ApiUnderstandingBenchmarkCase):
      prompt = self._create_prompt_for_api_understanding(benchmark_case)
      response_schema = ApiUnderstandingAnswerOutput
    elif isinstance(benchmark_case, MultipleChoiceBenchmarkCase):
      prompt = self._create_prompt_for_multiple_choice(benchmark_case)
      response_schema = MultipleChoiceAnswerOutput
    else:
      raise TypeError(
          f"Unsupported benchmark case type: {type(benchmark_case)}"
      )

    json_schema = response_schema.model_json_schema()

    # Remove benchmark_type from schema to prevent LLM confusion
    if (
        "properties" in json_schema
        and "benchmark_type" in json_schema["properties"]
    ):
      del json_schema["properties"]["benchmark_type"]
    if (
        "required" in json_schema
        and "benchmark_type" in json_schema["required"]
    ):
      json_schema["required"].remove("benchmark_type")

    response = await self.client.models.generate_content(
        model=self.model_name,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": json_schema,
        },
    )

    output = response_schema.model_validate_json(response.text)

    # Populate trace_logs with the full response metadata (usage, safety ratings, etc.)
    trace_logs = [
        TraceLogEvent(
            type="GEMINI_API_RESPONSE",
            content=response.text,
            details=response.model_dump(),
        )
    ]

    usage_metadata = None
    if response.usage_metadata:
      usage_metadata = UsageMetadata(
          total_tokens=response.usage_metadata.total_token_count,
          prompt_tokens=response.usage_metadata.prompt_token_count,
          completion_tokens=response.usage_metadata.candidates_token_count,
      )

    return GeneratedAnswer(
        output=output, trace_logs=trace_logs, usage_metadata=usage_metadata
    )

  def _get_llm_context_from_file(self, file_path: Path) -> str:
    """Reads a file and extracts the content between LLM_CONTEXT_BEGIN and LLM_CONTEXT_END tags."""
    with open(file_path, "r", encoding="utf-8") as f:
      lines = f.readlines()

    try:
      start_index = -1
      end_index = -1
      for i, line in enumerate(lines):
        if "# LLM_CONTEXT_BEGIN" in line:
          start_index = i + 1
        if "# LLM_CONTEXT_END" in line:
          end_index = i
          break

      if start_index == -1 or end_index == -1:
        return ""

      return "".join(lines[start_index:end_index])
    except ValueError as e:
      raise ValueError(
          "Could not find # LLM_CONTEXT_BEGIN or # LLM_CONTEXT_END tags in"
          f" {file_path}"
      ) from e

  def _create_prompt_for_fix_error(self, case: FixErrorBenchmarkCase) -> str:
    """Creates a prompt for a fix_error benchmark case."""
    prompt = (
        "You are an expert Python software engineer specializing in the ADK"
        " (Agent Development Kit) framework. Your task is to fix or implement"
        " the provided Python file content. You must provide the complete,"
        " corrected code for the entire file in the `code` field of the JSON"
        " output. CRITICAL: Your output MUST define a function with the exact"
        " signature: `def create_agent(model_name: str) -> BaseAgent:` DO NOT"
        " include any other functions or classes in your output unless they"
        " are part of the original unfixed file that you are fixing. The code"
        " should be a complete and valid Python file and **must include all"
        " necessary imports** for the code to function correctly."
        " Specifically:\n\n1.  **`MODEL_NAME`, `basic_tool`,"
        " `BasicOutputSchema`, `create_basic_llm_agent`, and `run_agent_test`"
        " are automatically available from `benchmarks.test_helpers` and DO"
        " NOT require explicit import statements within your generated code"
        " block.**\n2.  **All ADK agents (like `LlmAgent`, `SequentialAgent`,"
        " `ParallelAgent`, `LoopAgent`) MUST be initialized with a `name`"
        " argument.** The `LlmAgent` also REQUIRES a `model` argument (you can"
        " use the `model_name` variable passed to the `create_agent` function;"
        " do NOT quote it, e.g., `model=model_name`).\n3.  **The parameter for"
        " agent instructions is `instruction`, NOT `instructions`.**\n4. "
        " **Use helper functions from `benchmarks.test_helpers` where"
        " appropriate**, such as `create_basic_llm_agent`. Note: For this"
        " benchmark, you are primarily expected to implement the agent"
        " directly, so helper function usage might be minimal.\n5.  **DO NOT"
        " redefine core ADK classes** (e.g., `LlmAgent`, `App`, `Runner`,"
        " `BuiltInCodeExecutor`, `BasePlugin`) or other test helper components"
        " unless the task explicitly asks you to implement a *custom* class"
        " that *inherits* from an ADK base class (e.g., inheriting `BaseAgent`"
        " or `BasePlugin`).\n6.  **When initializing `FunctionTool`, use the"
        " argument `func` to pass the callable, not `fn`.**\n7.  **Your output"
        " should ONLY be the Python code for the function definition.** Do not"
        " include any other code, functions, or classes outside the"
        " function.\n8.  **When creating a `SequentialAgent`, `ParallelAgent`,"
        " or `LoopAgent`, the list of sub-agents should be passed to the"
        " `sub_agents` parameter.**\n9.  **When creating a `LoopAgent`, the"
        " number of iterations should be passed to the `max_iterations`"
        " parameter.**\n10. **`FunctionTool` does not accept a `name`"
        " argument.** The tool's name is inferred from the function"
        " itself.\n11. **When implementing a custom agent's `_call` method,"
        " you must use `async for` to iterate over and `yield` events from"
        " sub-agents.** Do not use `yield from` with async generators.\n12."
        " **If you define a custom agent class, you must instantiate it and"
        " assign it to the variable specified in the `requirements` (usually"
        " by returning it from the function).**\n13. **All plugins that"
        " inherit from `BasePlugin` must be initialized with a `name`"
        " argument.**\n14. **The `App` class requires a `name` argument upon"
        " initialization.**\n15. **When using `input_schema`, the fields from"
        " the schema are available to the model in the user's message.** Do"
        " not use `{field_name}` templating in the instruction string; the"
        " model will extract the values from the input content.\n\nHere is the"
        " detailed description of what the function should do:"
        f" {case.description}\n\n"
    )

    if case.requirements:
      prompt += "The generated code must satisfy the following requirements:\n"
      for req in case.requirements:
        prompt += f"- {req}\n"
      prompt += "\n"

    # Use unfixed_file for context
    if not case.unfixed_file:
      raise ValueError("unfixed_file not specified in benchmark case.")

    if not case.unfixed_file.exists():
      raise FileNotFoundError(f"Unfixed file not found: {case.unfixed_file}")

    full_unfixed_content = case.unfixed_file.read_text(encoding="utf-8")

    prompt += (
        "Here is the full content of the file where you need to fix the"
        f" `create_agent` function.\n```python\n{full_unfixed_content}\n```"
    )
    return prompt

  def _create_prompt_for_multiple_choice(
      self, case: MultipleChoiceBenchmarkCase
  ) -> str:
    """Creates a prompt for a multiple choice benchmark case."""
    options_str = "\n".join(
        f"{key}: {value}" for key, value in case.options.items()
    )
    prompt = (
        "You are an expert on the Google ADK Python framework. Answer the"
        " following multiple choice question. Return the result as a JSON"
        " object with a key 'answer' containing the single letter of the"
        " correct option (e.g., 'A', 'B', 'C', or 'D') and a key 'rationale'"
        " explaining your reasoning.\n\n"
    )

    context_content = self._get_context_content()
    if context_content:
      prompt += f"Context:\n{context_content}\n\n"

    if case.code_snippet_ref:
      try:
        code_content = load_snippet(case.code_snippet_ref)
        prompt += f"Code:\n```python\n{code_content}\n```\n\n"
      except Exception as e:
        # Warning: Failed to load code snippet. The model will not have this context.
        pass

    prompt += f"Question: {case.question}\n\nOptions:\n{options_str}\n"
    return prompt

  def _create_prompt_for_api_understanding(
      self, case: ApiUnderstandingBenchmarkCase
  ) -> str:
    """Creates a prompt for an api_understanding benchmark case."""
    template_info = TEMPLATES[case.template]
    examples = "\n".join(f"- {example}" for example in template_info.examples)
    prompt = (
        "You are an expert software engineer specializing in the Google ADK"
        " Python framework. Your task is to identify the precise and exact"
        " Python definition from the ADK API that correctly answers the"
        " following question. The definition must conform to the specified"
        " template structure. Return the result as a JSON object with three"
        " keys. First, 'code' for the resulting definition. If the template"
        " specifies an identifier (e.g., a parameter, class, or method name),"
        " ensure 'code' contains *only* that identifier (e.g.,"
        " 'parameter_name', not 'parameter_name: str'). If the question asks"
        " for a specific named tool (like GoogleSearchTool), 'code' should be"
        " the exact class name of that tool. Second,"
        " 'fully_qualified_class_name' for the fully qualified name of the"
        " *class* where the API element is defined (do not include method or"
        " parameter names in the fully qualified class name). Third,"
        " 'rationale' explaining your reasoning.\n\n"
    )

    context_content = self._get_context_content()
    if context_content:
      prompt += f"Context:\n{context_content}\n\n"

    prompt += (
        "Here are a few examples:\n\nQuestion: What is the main class for"
        " creating a sequential agent in the ADK?\nRationale: The user is"
        " asking for the primary class to instantiate a sequential"
        " agent.\nTemplate:"
        f' "{TEMPLATES[AnswerTemplate.CLASS_DEFINITION].description}"\nAnswer:'
        ' \n```json\n{\n    "code": "class'
        ' SequentialAgent(google.adk.agents.agent.Agent):",\n   '
        ' "fully_qualified_class_name":'
        ' "google.adk.agents.sequential_agent.SequentialAgent",\n   '
        ' "rationale": "The user is asking for the primary class to'
        ' instantiate a sequential agent."\n}\n```\n\nQuestion: Which method'
        " is used to execute an agent in the ADK?\nRationale: The user wants"
        " to know the function to run an agent.\nTemplate:"
        f' "{TEMPLATES[AnswerTemplate.METHOD_DEFINITION].description}"\nAnswer:'
        ' \n```json\n{\n    "code": "def run(self, request: "RunnerRequest")'
        ' -> "RunnerResponse":",\n    "fully_qualified_class_name":'
        ' "google.adk.runners.Runner",\n    "rationale": "The user wants to'
        ' know the function to run an agent."\n}\n```\n\nQuestion: What'
        " parameter defines the LLM to be used in an LlmAgent?\nRationale: The"
        " user needs to identify the specific parameter for setting the"
        " language model in an LlmAgent.\nTemplate:"
        f' "{TEMPLATES[AnswerTemplate.PARAMETER_DEFINITION].description}"\nAnswer:'
        ' \n```json\n{\n    "code": "model",\n   '
        ' "fully_qualified_class_name":'
        ' "google.adk.agents.llm_agent.LlmAgent",\n    "rationale": "The user'
        " needs to identify the specific parameter for setting the language"
        ' model in an LlmAgent."\n}\n```\n\nQuestion: Which specific tool'
        " class in ADK leverages Google's native search capability?Rationale:"
        " The user is asking for the specific class that integrates Google"
        " Search natively.Template:"
        f' "{TEMPLATES[AnswerTemplate.CLASS_DEFINITION].description}"\nAnswer:'
        ' \n```json\n{\n    "code": "GoogleSearchTool",\n   '
        ' "fully_qualified_class_name":'
        ' "google.adk.tools.google_search_tool.GoogleSearchTool",\n   '
        ' "rationale": "The user is asking for the specific class that'
        ' integrates Google Search natively."\n}\n```\n\nQuestion: Which'
        " class is used to run multiple agents concurrently in ADK?Rationale:"
        " The user is asking for the class that enables parallel execution of"
        " agents.Template:"
        f' "{TEMPLATES[AnswerTemplate.CLASS_DEFINITION].description}"\nAnswer:'
        ' \n```json\n{\n    "code": "ParallelAgent",\n   '
        ' "fully_qualified_class_name":'
        ' "google.adk.agents.parallel_agent.ParallelAgent",\n    "rationale":'
        ' "The user is asking for the class that enables parallel execution of'
        ' agents."\n}\n```\n\nNow, answer the following'
        f" question:\n\nQuestion: {case.question}\nTemplate:"
        f" {template_info.description}\nExamples:\n{examples}\n"
    )
    return prompt
