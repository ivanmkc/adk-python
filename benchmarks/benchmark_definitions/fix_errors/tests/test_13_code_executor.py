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

"""13: An LlmAgent with a BuiltInCodeExecutor."""
from __future__ import annotations

from benchmarks.test_helpers import run_agent_test
from benchmarks.test_helpers import MODEL_NAME

# LLM_CONTEXT_BEGIN
from google.adk.agents import LlmAgent
from google.adk.code_executors.built_in_code_executor import BuiltInCodeExecutor

# BEGIN: CODE
root_agent = LlmAgent(
    name="code_exec_agent",
    model=MODEL_NAME,
    instruction="You are a helpful assistant. Use the code executor to calculate 2 + 2.",
    code_executor=BuiltInCodeExecutor(),
)
# END: CODE
# LLM_CONTEXT_END


async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "Calculate 2 + 2.", mock_llm_response="4")


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    assert "4" in response


async def test_code_executor():
    """Tests that an agent can execute a simple Python code block."""
    response = await run_test()
    assert_test(response)
