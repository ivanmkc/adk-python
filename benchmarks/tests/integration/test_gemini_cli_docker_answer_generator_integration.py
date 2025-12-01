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

import pytest
import os
import subprocess
import json
from pathlib import Path
from benchmarks.answer_generators.gemini_cli_docker_answer_generator import GeminiCliDockerAnswerGenerator
from benchmarks.data_models import MultipleChoiceBenchmarkCase

# Helper to get image name (duplicated from candidates for test isolation)
def get_docker_image_name():
    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or \
                     subprocess.check_output(["gcloud", "config", "get-value", "project"], text=True).strip()
        return f"gcr.io/{project_id}/adk-gemini-sandbox:latest"
    except:
        return "adk-gemini-sandbox:latest"

DOCKER_IMAGE = get_docker_image_name()

def docker_available():
    try:
        subprocess.run(["docker", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

@pytest.mark.asyncio
@pytest.mark.skipif(not docker_available(), reason="Docker not available")
async def test_docker_generator_integration_simple_math(tmp_path):
    """
    Runs a real integration test against the Docker container.
    Verifies that we can talk to the container and get a valid JSON response.
    """

    # Ensure we have credentials to pass
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_GENAI_USE_VERTEXAI"):
        pytest.skip("No API credentials (GEMINI_API_KEY or VERTEX AI vars) found in environment.")

    # Create a dummy context file
    context_file = tmp_path / "context.txt"
    context_file.write_text("This is a dummy context.")

    generator = GeminiCliDockerAnswerGenerator(
        model_name="gemini-2.5-flash",
        image_name="adk-gemini-sandbox:adk-python",
        context=context_file,
    )

    print(f"\nTesting with Docker image: {DOCKER_IMAGE}")
    case = MultipleChoiceBenchmarkCase(
        question="What is 2 + 2?",
        options={"A": "3", "B": "4", "C": "5"},
        correct_answer="B",
        benchmark_type="multiple_choice",
        explanation="Math."
    )

    try:
        result = await generator.generate_answer(case)
        print(f"\nGenerated Answer: {result.output.answer}")
        print(f"Rationale: {result.output.rationale}")

        assert result.output.answer in ["B", "4"], f"Expected B or 4, got {result.output.answer}"
        assert result.output.rationale, "Rationale should not be empty"
        
        # Check trace logs
        assert result.output.trace_logs, "Trace logs should not be empty"
        assert "--- DOCKER STDOUT ---" in result.output.trace_logs, "Trace logs should contain Docker output header"

    except RuntimeError as e:
        # If the image is missing, we might get a specific error. 
        if "Unable to find image" in str(e) or "pull access denied" in str(e):
             pytest.fail(f"Could not pull/find Docker image {DOCKER_IMAGE}. Please ensure it is built/pushed.\nError: {e}")
        else:
             pytest.fail(f"Docker execution failed: {e}")

