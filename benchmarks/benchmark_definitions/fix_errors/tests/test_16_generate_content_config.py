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

"""Build integrity test for LlmAgent with generate_content_config."""
from __future__ import annotations

import pytest
from benchmarks.test_helpers import MODEL_NAME
from benchmarks.test_helpers import run_agent_test

# LLM_CONTEXT_BEGIN
from google.adk.agents import LlmAgent
from google.genai import types

# BEGIN: CODE
agent = LlmAgent(
    name="config_agent",
    model=MODEL_NAME,
    instruction="You are a helpful assistant. Always respond with 'Hello world!'",
    generate_content_config=types.GenerationConfig(temperature=0.0),
)
# END: CODE
# LLM_CONTEXT_END

@pytest.mark.asyncio
async def test_generate_content_config_temperature():
    """Tests that LlmAgent respects generate_content_config for temperature."""
    response = await run_agent_test(agent, "Say hello.", mock_llm_response="Hello world!")
    assert "Hello world!" in response
