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
from google.adk.agents import LlmAgent, Agent
from google.adk.testing import AgentTest
import asyncio

# LLM_CONTEXT_BEGIN
# The following code block contains incorrect API usage for LlmAgent.
# Fix it to define a valid LlmAgent that uses the correct parameter for instruction.

# BEGIN: CODE
root_agent = LlmAgent(
    name='api_agent',
    model='gemini-2.5-flash',
    instructions='You are a helpful assistant.' # Incorrect parameter name
)
# END: CODE
# LLM_CONTEXT_END

@pytest.mark.asyncio
async def test_incorrect_api_usage_agent():
    assert isinstance(root_agent, Agent), "root_agent should be an instance of Agent"
    test = AgentTest(agent=root_agent)
    response = await test.send_message("Hello")
    assert "Hello" in response.text, "Agent should respond to 'Hello' with 'Hello'"
