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

"""04: A SequentialAgent orchestrating two simple agents."""
from __future__ import annotations

import pytest

from benchmarks.test_helpers import run_agent_test
from benchmarks.test_helpers import MODEL_NAME

# LLM_CONTEXT_BEGIN
from google.adk.agents import LlmAgent, SequentialAgent

# BEGIN: CODE
agent_one = LlmAgent(
    name="agent_one",
    model=MODEL_NAME,
    instruction="This is the first agent. Respond with 'one'."
)
agent_two = LlmAgent(
    name="agent_two",
    model=MODEL_NAME,
    instruction="This is the second agent. Respond with 'two'."
)

root_agent = SequentialAgent(
    name="sequential_coordinator", sub_agents=[agent_one, agent_two]
)
# END: CODE
# LLM_CONTEXT_END


async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "Run the sequence.")


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    # The final response should be from the last agent in the sequence.
    assert "two" in response.lower()


async def test_sequential_agent():
    """Tests that a sequential agent executes its sub-agents in order."""
    response = await run_test()
    assert_test(response)
