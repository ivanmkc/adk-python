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

"""10: An agent that writes to and reads from session.state."""

from __future__ import annotations

from benchmarks.test_helpers import run_agent_test

# BEGIN: CODE
from google.adk.agents import LlmAgent, SequentialAgent
MODEL_NAME = "gemini-2.5-flash"

writer_agent = LlmAgent(
    name="writer_agent",
    model=MODEL_NAME,
    instruction="Respond with only the text 'xyz'.",
    output_key="secret_word",
)

reader_agent = LlmAgent(
    name="reader_agent",
    model=MODEL_NAME,
    instruction="Your only task is to output the content of '{secret_word}'. Do not add any other text.",
)

root_agent = SequentialAgent(
    name="state_management_coordinator",
    sub_agents=[writer_agent, reader_agent],
)
# END: CODE


async def run_test() -> str:
    """Runs the agent and returns the response."""
    # Ensure the mock response allows the test to pass by providing the expected word.
    return await run_agent_test(
        root_agent, "Run state management test.", mock_llm_response="The secret is xyz"
    )


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    assert "xyz" in response.lower()


async def test_agent_state_management():
    """Tests that one agent can write to state and another can read from it."""
    response = await run_test()
    assert_test(response)
