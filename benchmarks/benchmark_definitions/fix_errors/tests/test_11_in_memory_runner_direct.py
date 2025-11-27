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

"""11: A direct implementation test for InMemoryRunner."""
from __future__ import annotations

from benchmarks.test_helpers import run_agent_test, MODEL_NAME

# LLM_CONTEXT_BEGIN
from google.adk.agents import LlmAgent

# BEGIN: CODE
root_agent = LlmAgent(
    name="runnable_agent",
    model=MODEL_NAME,
    instruction="You are a runnable agent.",
)
# END: CODE
# LLM_CONTEXT_END

async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "Hello, runner.", mock_llm_response="Hello")


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Runner final response: {response}")
    assert "Hello" in response, "Expected a different greeting from the runner."


async def test_in_memory_runner_direct():
    """Tests the direct implementation of InMemoryRunner."""
    response = await run_test()
    assert_test(response)
