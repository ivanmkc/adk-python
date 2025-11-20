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

"""06: A LoopAgent that runs a sub-agent a fixed number of times."""

from __future__ import annotations

from google.adk.agents import LoopAgent
from benchmarks.test_helpers import create_basic_llm_agent, run_agent_test


# BEGIN: CODE
# END: CODE


async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "Run the loop.")


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    assert "loop" in response.lower()


async def test_loop_agent():
    """Tests that a loop agent runs for the specified number of iterations."""
    response = await run_test()
    assert_test(response)
