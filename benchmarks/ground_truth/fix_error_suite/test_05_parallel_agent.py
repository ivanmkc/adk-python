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

"""05: A ParallelAgent running two agents concurrently."""

from __future__ import annotations

import pytest
from google.adk.agents import ParallelAgent
from benchmarks.test_helpers import create_basic_llm_agent, run_agent_test


# BEGIN: CODE
agent_one = create_basic_llm_agent(
    name="agent_one",
    instruction="Respond with only the text: This is the first parallel agent.",
)
agent_two = create_basic_llm_agent(
    name="agent_two",
    instruction="Respond with only the text: This is the second parallel agent.",
)

root_agent = ParallelAgent(
    name="parallel_coordinator", sub_agents=[agent_one, agent_two]
)
# END: CODE


async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "Run in parallel.")


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    # The response could be from either agent, so we check for a common word.
    assert "parallel" in response.lower()


async def test_parallel_agent():
    """Tests that a parallel agent executes its sub-agents."""
    response = await run_test()
    assert_test(response)
