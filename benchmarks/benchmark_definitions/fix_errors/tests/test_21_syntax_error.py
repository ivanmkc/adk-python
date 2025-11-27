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
from benchmarks.test_helpers import run_agent_test
import asyncio

# LLM_CONTEXT_BEGIN
# The following code block contains a syntax error.
# Fix it to define a valid LlmAgent.

# BEGIN: CODE
root_agent = LlmAgent(name='syntax_agent', model='gemini-2.5-flash', instruction='You are a helpful assistant.')
# END: CODE
# LLM_CONTEXT_END

@pytest.mark.asyncio
async def test_syntax_error_agent():
    assert isinstance(root_agent, Agent), "root_agent should be an instance of Agent"
    response = await run_agent_test(root_agent, "Hello", mock_llm_response="Hello")
    assert "Hello" in response, "Agent should respond to 'Hello' with 'Hello'"