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

"""02: An LlmAgent with a simple function tool."""

from __future__ import annotations

import pytest
from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from benchmarks.test_helpers import MODEL_NAME, basic_tool, run_agent_test


# BEGIN: CODE
root_agent = LlmAgent(
    name="tool_agent",
    model=MODEL_NAME,
    instruction="Use the `basic_tool` with the query 'test'.",
    tools=[FunctionTool(func=basic_tool)],
)
# END: CODE


async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "Can you use your tool?")


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    assert "test" in response.lower()


async def test_agent_with_tool():
    """Tests that an agent can use a simple tool."""
    response = await run_test()
    assert_test(response)
