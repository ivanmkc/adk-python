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
"""11: A direct implementation test for InMemoryRunner."""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types

from benchmarks.test_helpers import MODEL_NAME


async def run_test() -> str:
    """Runs the agent and returns the response."""
    # BEGIN: CODE
    agent = LlmAgent(
        name="runnable_agent",
        model=MODEL_NAME,
        instruction="You are a runnable agent.",
    )
    # END: CODE
    app = App(name="runner_test_app", root_agent=agent)
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        app_name=app.name, user_id="test-user"
    )

    final_response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="Hello, runner.")]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text
    return final_response


# LLM_CONTEXT_END


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Runner final response: {response}")
    assert "Hello" in response, "Expected a different greeting from the runner."


async def test_in_memory_runner_direct():
    """Tests the direct implementation of InMemoryRunner."""
    response = await run_test()
    assert_test(response)
