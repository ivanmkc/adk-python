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

"""Build integrity test for LlmAgent with input_schema."""
from __future__ import annotations

import pytest
from pydantic import BaseModel, Field

from benchmarks.test_helpers import MODEL_NAME
from benchmarks.test_helpers import run_agent_test

# LLM_CONTEXT_BEGIN
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

class UserInfo(BaseModel):
    name: str = Field(description="The user's name.")
    age: int = Field(description="The user's age.")

# BEGIN: CODE
worker_agent = LlmAgent(
    name="worker",
    model=MODEL_NAME,
    instruction="Acknowledge the user's name and age.",
    input_schema=UserInfo,
)
agent = LlmAgent(
    name="agent",
    model=MODEL_NAME,
    tools=[AgentTool(agent=worker_agent)],
    instruction="Use the worker agent to process the user's info.",
)
# END: CODE
# LLM_CONTEXT_END

@pytest.mark.asyncio
async def test_input_schema_validation():
    """Tests that LlmAgent respects input_schema for structured input."""
    response = await run_agent_test(
        agent, 'Process this info: name is Alice, age is 30'
    )
    assert "Alice" in response and "30" in response

    response_invalid = await run_agent_test(
        agent, 'Process this info: name is Bob'
    )
    # The model should ideally return a response indicating an error.
    # Checking for "error" is a reasonable expectation.
    assert "age" in response_invalid.lower()
