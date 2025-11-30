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
import json
from unittest.mock import MagicMock, patch, AsyncMock
from benchmarks.answer_generators.gemini_cli_docker_answer_generator import GeminiCliDockerAnswerGenerator
from benchmarks.data_models import ApiUnderstandingBenchmarkCase, AnswerTemplate

@pytest.mark.asyncio
async def test_docker_command_construction_api_key():
    """Test that Docker command is constructed correctly with GEMINI_API_KEY."""
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
        generator = GeminiCliDockerAnswerGenerator(
            model_name="gemini-2.5-flash",
            image_name="my-image:latest"
        )
        
        # Valid inner JSON response (Raw text output from CLI)
        model_output = {
            "code": "class Test:",
            "fully_qualified_class_name": "test.Test",
            "rationale": "Because."
        }
        # Since we removed --output-format json, the CLI outputs the raw text.
        # So we simply dump the model output as the stdout bytes.
        stdout_bytes = json.dumps(model_output).encode()
        
        # Mock the subprocess execution
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_proc = MagicMock()
            mock_proc.communicate = AsyncMock(return_value=(stdout_bytes, b""))
            mock_proc.returncode = 0
            mock_exec.return_value = mock_proc
            
            # Create a dummy case
            case = ApiUnderstandingBenchmarkCase(
                name="Test", description="Test", category="Test", 
                question="Test question", rationale="Test", file="test.py", 
                template=AnswerTemplate.CLASS_DEFINITION, answers=[]
            )
            
            await generator.generate_answer(case)
            
            # Verify call arguments
            args = mock_exec.call_args[0]
            
            # Expect: docker run --rm -e GEMINI_API_KEY my-image:latest gemini ...
            assert args[0] == "docker"
            assert args[1] == "run"
            assert "-e" in args
            assert "GEMINI_API_KEY" in args
            assert "my-image:latest" in args
            assert "gemini" in args  # The inner command
            assert "--sandbox" not in args # Should NOT have --sandbox flag

@pytest.mark.asyncio
async def test_docker_command_construction_vertex_adc():
    """Test that Docker command handles Vertex AI and ADC mounting correctly."""
    
    env_vars = {
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
        "GOOGLE_CLOUD_PROJECT": "my-project",
        "GOOGLE_APPLICATION_CREDENTIALS": "/local/path/creds.json"
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        generator = GeminiCliDockerAnswerGenerator(image_name="my-image:latest")
        
        # Valid inner JSON response (Raw text output from CLI)
        model_output = {
            "code": "class Vertex:",
            "fully_qualified_class_name": "vertex.Test",
            "rationale": "Vertex logic."
        }
        stdout_bytes = json.dumps(model_output).encode()
        
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_proc = MagicMock()
            mock_proc.communicate = AsyncMock(return_value=(stdout_bytes, b""))
            mock_proc.returncode = 0
            mock_exec.return_value = mock_proc
            
            case = ApiUnderstandingBenchmarkCase(
                name="Test", description="Test", category="Test", 
                question="Test", rationale="Test", file="test.py", 
                template=AnswerTemplate.CLASS_DEFINITION, answers=[]
            )
            
            await generator.generate_answer(case)
            
            args = mock_exec.call_args[0]
            
            # Check for env vars passing
            assert "GOOGLE_GENAI_USE_VERTEXAI" in args
            assert "GOOGLE_CLOUD_PROJECT" in args
            
            # Check for volume mount
            # Should find -v /local/path/creds.json:/tmp/google_credentials.json
            assert "-v" in args
            volume_arg_idx = args.index("-v") + 1
            assert args[volume_arg_idx] == "/local/path/creds.json:/tmp/google_credentials.json"
            
            # Check environment var mapping in container
            assert "GOOGLE_APPLICATION_CREDENTIALS=/tmp/google_credentials.json" in [
                arg for arg in args if arg.startswith("GOOGLE_APPLICATION_CREDENTIALS=")
            ]
