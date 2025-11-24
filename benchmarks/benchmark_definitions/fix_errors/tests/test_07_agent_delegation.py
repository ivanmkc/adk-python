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

# LLM_CONTEXT_BEGIN
"""07: A root agent delegating a task to a sub-agent."""

from __future__ import annotations

from google.adk.agents import LlmAgent

from benchmarks.test_helpers import MODEL_NAME
from benchmarks.test_helpers import run_agent_test

# BEGIN: CODE
specialist_agent = LlmAgent(
    name="specialist_agent",
    model=MODEL_NAME,
    instruction="You are a specialist. You only respond with 'specialist ok'.",
    description="Use this agent for specialist tasks.",
)

root_agent = LlmAgent(
    name="delegator_agent",
    model=MODEL_NAME,
    sub_agents=[specialist_agent],
    instruction=(
        "You are a delegator. If the user asks for a specialist, delegate the"
        " task to the 'specialist_agent'."
    ),
)
# END: CODE
# LLM_CONTEXT_END


async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "I need a specialist.")


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    assert "specialist ok" in response.lower()


async def test_agent_delegation():
    """Tests that a root agent can delegate a task to a sub-agent."""
    response = await run_test()
    assert_test(response)
