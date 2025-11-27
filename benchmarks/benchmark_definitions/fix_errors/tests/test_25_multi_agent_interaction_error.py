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
from google.adk.agents import LlmAgent, SequentialAgent, Agent
from google.adk.testing import AgentTest
import asyncio

# LLM_CONTEXT_BEGIN
# The following code block contains an error in multi-agent interaction.
# Fix the `SequentialAgent` configuration so that the `reader_agent` correctly receives
# the output from the `writer_agent` via the session state.

# BEGIN: CODE
MODEL_NAME = "gemini-2.5-flash"

writer_agent = LlmAgent(
    name="writer_agent",
    model=MODEL_NAME,
    instruction="Respond with only the text 'secret_message'.",
    output_key="wrong_key", # Incorrect output key
)

reader_agent = LlmAgent(
    name="reader_agent",
    model=MODEL_NAME,
    instruction="Your only task is to output the content of '{correct_key}'. Do not add any other text.",
)

root_agent = SequentialAgent(
    name="multi_agent_coordinator",
    sub_agents=[writer_agent, reader_agent],
)
# END: CODE
# LLM_CONTEXT_END

@pytest.mark.asyncio
async def test_multi_agent_interaction_error():
    assert isinstance(root_agent, Agent), "root_agent should be an instance of Agent"
    test = AgentTest(agent=root_agent)
    response = await test.send_message("Start interaction")
    assert "secret_message" in response.text, "Reader agent should output 'secret_message'"
