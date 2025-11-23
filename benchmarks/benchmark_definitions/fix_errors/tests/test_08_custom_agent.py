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
"""08: A simple custom agent with conditional logic."""

from __future__ import annotations

from typing import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from benchmarks.test_helpers import create_basic_llm_agent, run_agent_test


# BEGIN: CODE
# END: CODE
# LLM_CONTEXT_END


async def run_test(run_a: bool) -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "Run", initial_state={"run_agent_a": run_a})


def assert_test(response: str, expected_agent: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    assert expected_agent in response


async def test_custom_agent_condition_a():
    """Tests that the custom agent runs agent_a when the condition is met."""
    response = await run_test(run_a=True)
    assert_test(response, "Agent A")


async def test_custom_agent_condition_b():
    """Tests that the custom agent runs agent_b when the condition is not met."""
    response = await run_test(run_a=False)
    assert_test(response, "Agent B")
