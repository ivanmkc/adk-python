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

"""Build integrity test for LlmAgent with expanded callbacks."""

from __future__ import annotations

import pytest

from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from benchmarks._rigs import MODEL_NAME, run_agent_test


async def _mock_tool_func(query: str) -> str:
  return f"UNIQUE_TOOL_OUTPUT_FOR_TEST: {query}"


@pytest.mark.asyncio
async def test_before_and_after_tool_callbacks():
  """Tests that before_tool_callback and after_tool_callback are invoked."""
  before_called = []
  after_called = []

  async def before_callback_func(tool, args, tool_context):
    before_called.append(True)
    return None  # Do not modify tool args

  async def after_callback_func(tool, args, tool_context, tool_response):
    after_called.append(True)
    return None  # Do not modify tool response

  test_tool = FunctionTool(func=_mock_tool_func)

  # BEGIN: CODE
  agent = LlmAgent(
      name="callback_agent",
      model=MODEL_NAME,
      instruction="Use the test_tool to respond to the user. Return the tool's output verbatim.",
      tools=[test_tool],
      before_tool_callbacks=before_callback_func,
      after_tool_callback=after_callback_func,
  )
  # END: CODE

  response = await run_agent_test(agent, "Use the tool with 'hello'")

  assert before_called
  assert after_called
  assert "UNIQUE_TOOL_OUTPUT_FOR_TEST: hello" in response
