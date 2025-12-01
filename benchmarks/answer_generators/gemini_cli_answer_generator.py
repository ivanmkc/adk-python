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

"""An AnswerGenerator that uses the gemini CLI to generate answers."""

import asyncio
import json
import re
from pathlib import Path
from typing import Any

from benchmarks.answer_generators.gemini_answer_generator import GeminiAnswerGenerator
from benchmarks.data_models import ApiUnderstandingAnswerOutput
from benchmarks.data_models import ApiUnderstandingBenchmarkCase
from benchmarks.data_models import BaseBenchmarkCase
from benchmarks.data_models import FixErrorAnswerOutput
from benchmarks.data_models import FixErrorBenchmarkCase
from benchmarks.data_models import GeneratedAnswer
from benchmarks.data_models import MultipleChoiceAnswerOutput
from benchmarks.data_models import MultipleChoiceBenchmarkCase


class GeminiCliAnswerGenerator(GeminiAnswerGenerator):
    """An AnswerGenerator that uses the gemini CLI programmatically."""

    def __init__(
        self,
        model_name: str = "gemini-2.5-pro",
        context: str | Path | None = None,
        cli_path: str = "gemini",
    ):
        # Do not call super().__init__ to avoid initializing the genai client
        # effectively decoupling from the SDK client logic while reusing prompt logic.
        self.model_name = model_name
        self.context = context
        self.cli_path = cli_path

    @property
    def name(self) -> str:
        """Returns a unique name for this generator instance."""
        # Reuse parent naming logic but indicate CLI usage
        base = super().name
        return base.replace("GeminiAnswerGenerator", "GeminiCliAnswerGenerator")

    async def generate_answer(
        self,
        benchmark_case: BaseBenchmarkCase
    ) -> GeneratedAnswer:
        """Generates an answer using the gemini CLI."""
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
            raise TypeError(f"Unsupported benchmark case type: {type(benchmark_case)}")

        # Append explicit JSON enforcement instructions since CLI doesn't support response_schema
        schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
        prompt += (
            "\n\nIMPORTANT: You must output PURE JSON matching this schema. "
            "Do not include any markdown formatting, explanations, or code blocks outside the JSON object.\n"
            f"JSON Schema:\n{schema_json}\n"
        )

        # Run the CLI command
        cli_response, logs = await self._run_cli_command(prompt)

        # Extract the 'response' field which contains the model's text output
        model_text = cli_response.get("response", "")
        
        # The model's text output is expected to be a JSON string (because the prompt asks for it)
        # potentially wrapped in markdown code blocks.
        json_content = self._extract_json_from_text(model_text)
        
        try:
            # Parse the inner JSON content into the Pydantic model
            output = response_schema.model_validate_json(json_content)
            output.trace_logs = logs
        except Exception as e:
            # If parsing fails, wrap it in a generic error or re-raise
            # For now, we'll try to fail gracefully if possible, or just raise
            raise ValueError(f"Failed to parse structured output from CLI response: {e}\nOutput was: {model_text}") from e

        return GeneratedAnswer(output=output)

    async def _run_cli_command(self, prompt: str) -> tuple[dict[str, Any], str]:
        """Executes the gemini CLI command and returns the parsed JSON output and raw logs."""
        args = [
            self.cli_path,
            prompt,  # Pass prompt as positional argument
            "--output-format",
            "json",
            "--model",
            self.model_name,
            "--yolo",
            "--sandbox",
        ]

        # Create subprocess
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()
        
        stdout_str = stdout.decode()
        stderr_str = stderr.decode()
        logs = f"--- CLI STDOUT ---\n{stdout_str}\n--- CLI STDERR ---\n{stderr_str}"

        if proc.returncode != 0:
            error_msg = stderr_str.strip() or stdout_str.strip()
            raise RuntimeError(f"Gemini CLI failed with code {proc.returncode}: {error_msg}")

        try:
            return json.loads(stdout_str), logs
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON output from Gemini CLI: {e}\nStdout: {stdout_str}") from e

    def _extract_json_from_text(self, text: str) -> str:
        """Extracts JSON content from a string, handling markdown code blocks."""
        text = text.strip()
        
        # Match ```json ... ``` or just ``` ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        
        # If no code blocks, assume the whole text is JSON
        return text
