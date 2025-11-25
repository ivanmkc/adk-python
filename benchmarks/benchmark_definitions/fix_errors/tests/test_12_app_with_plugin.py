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

"""12: An App instance that includes a basic plugin."""
from __future__ import annotations

from benchmarks.test_helpers import run_agent_test
from benchmarks.test_helpers import MODEL_NAME

# LLM_CONTEXT_BEGIN
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.plugins import BasePlugin

# BEGIN: CODE
class SimplePlugin(BasePlugin):
    """A simple plugin that adds a prefix to the response."""

    def __init__(self) -> None:
        super().__init__(name="simple_plugin")

    async def after_agent_callback(self, **kwargs) -> None:
        # This is a simplified example. A real plugin would modify the event.
        print("SimplePlugin: after_agent_callback")


root_agent = LlmAgent(
    name="app_agent",
    model=MODEL_NAME,
    instruction="You are an agent within an App."
)

app = App(
    name="my_app",
    root_agent=root_agent,
    plugins=[SimplePlugin()],
)
# END: CODE
# LLM_CONTEXT_END


async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(app.root_agent, "Hello")


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    assert "Hello" in response


async def test_app_with_plugin():
    """Tests that an app with a plugin can run."""
    response = await run_test()
    assert_test(response)
