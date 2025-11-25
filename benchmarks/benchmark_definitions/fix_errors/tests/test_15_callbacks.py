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

"""15: An LlmAgent with an after_model_callback."""
from __future__ import annotations

from benchmarks.test_helpers import run_agent_test
from benchmarks.test_helpers import MODEL_NAME

callback_was_called = False

# LLM_CONTEXT_BEGIN
from google.adk.agents import LlmAgent

def my_callback(**kwargs):
    """A simple callback that sets a flag."""
    global callback_was_called
    callback_was_called = True
    print("Callback was executed.")


# BEGIN: CODE
root_agent = LlmAgent(
    name="callback_agent",
    model=MODEL_NAME,
    instruction="You are a helpful assistant.",
    after_model_callback=my_callback,
)
# END: CODE
# LLM_CONTEXT_END


async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "Hello")


def assert_test(response: str):
    """Asserts the response is valid and the callback was called."""
    print(f"Agent response: {response}")
    assert "Hello" in response
    assert callback_was_called, "The after_model_callback was not called."


async def test_after_model_callback():
    """Tests that the after_model_callback is triggered."""
    response = await run_test()
    assert_test(response)
