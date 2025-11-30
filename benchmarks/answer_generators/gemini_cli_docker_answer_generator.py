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

"""An AnswerGenerator that uses the gemini CLI inside a Docker container."""

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from benchmarks.answer_generators.gemini_cli_answer_generator import GeminiCliAnswerGenerator

class GeminiCliDockerAnswerGenerator(GeminiCliAnswerGenerator):
    """An AnswerGenerator that uses the gemini CLI inside a Docker container."""

    def __init__(
        self,
        model_name: str = "gemini-2.5-pro",
        context: str | Path | None = None,
        image_name: str = "adk-gemini-sandbox:latest",
    ):
        super().__init__(model_name=model_name, context=context, cli_path="gemini")
        self.image_name = image_name

    @property
    def name(self) -> str:
        """Returns a unique name for this generator instance."""
        base = super().name
        return base.replace("GeminiCliAnswerGenerator", "GeminiCliDockerAnswerGenerator")

    async def _run_cli_command(self, prompt: str) -> dict[str, Any]:
        """Executes the gemini CLI command inside Docker and returns the parsed JSON output."""
        
        # Prepend filesystem context instructions
        context_instruction = (
            "\nCONTEXT: You are working in a Docker container. "
            "The current working directory is `/repos`. "
            "The project source code is located in the subdirectory `./adk-python`. "
            "You MUST look into `./adk-python` to find source files, tests, or configuration.\n\n"
        )
        full_prompt = context_instruction + prompt

        # Prepare Docker command
        # We need to run the container, pass auth env vars, and execute the gemini command.
        
        docker_args = ["docker", "run", "--rm"]

        # Handle Authentication
        # 1. Check for GEMINI_API_KEY
        if os.environ.get("GEMINI_API_KEY"):
            docker_args.extend(["-e", "GEMINI_API_KEY"])
        
        # 2. Check for Vertex AI params
        if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI"):
            docker_args.extend(["-e", "GOOGLE_GENAI_USE_VERTEXAI"])
            if os.environ.get("GOOGLE_API_KEY"):
                docker_args.extend(["-e", "GOOGLE_API_KEY"])
            if os.environ.get("GOOGLE_CLOUD_PROJECT"):
                 docker_args.extend(["-e", "GOOGLE_CLOUD_PROJECT"])
            if os.environ.get("GOOGLE_CLOUD_LOCATION"):
                 docker_args.extend(["-e", "GOOGLE_CLOUD_LOCATION"])
            
            # Handle ADC file mapping
            adc_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if adc_path:
                # We must mount the file into the container
                # Use a fixed path inside the container to avoid path issues
                container_adc_path = "/tmp/google_credentials.json"
                docker_args.extend(["-v", f"{adc_path}:{container_adc_path}"])
                docker_args.extend(["-e", f"GOOGLE_APPLICATION_CREDENTIALS={container_adc_path}"])

        # Docker Image
        docker_args.append(self.image_name)

        # Gemini Command (inside container)
        # Note: we use the same arguments as the base class, but 'gemini' is the entrypoint or command
        gemini_args = [
            self.cli_path, # "gemini"
            full_prompt,
            # "--output-format", "json",  <-- Removed: unsupported
            "--model", self.model_name,
            "--yolo",
            # "--sandbox",  <-- Removed because we are already in a container
        ]        
        # The base class _run_cli_command hardcodes the args. 
        # I cannot easily reuse it without copy-pasting or modifying the base class.
        # I will copy-paste the logic but adapt the args.
        
        # Construct the full command arguments
        cmd_args = docker_args + gemini_args

        # Create subprocess
        proc = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode().strip() or stdout.decode().strip()
            raise RuntimeError(f"Gemini CLI (Docker) failed with code {proc.returncode}: {error_msg}")

        # Since we removed --output-format json, the CLI returns raw text (or markdown).
        # We manually wrap it to match the expected format of the base class.
        raw_output = stdout.decode().strip()
        return {"response": raw_output}

        # try:
        #     return json.loads(stdout.decode())
        # except json.JSONDecodeError as e:
        #     raise RuntimeError(f"Failed to parse JSON output from Gemini CLI (Docker): {e}\nStdout: {stdout.decode()}") from e
