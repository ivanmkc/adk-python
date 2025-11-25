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

from unittest.mock import patch

from google.adk.apps import App
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import InMemoryRunner
from google.genai import types
import pytest

from benchmarks.test_helpers import MODEL_NAME


async def _mock_tool_func(query: str) -> str:
    return f"UNIQUE_TOOL_OUTPUT_FOR_TEST: {query}"


# LLM_CONTEXT_BEGIN
from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool

# BEGIN: CODE
# The callbacks need to be defined here since they are directly referenced by the agent.
# We will use placeholders for them and define the actual functions in the test.

root_agent = LlmAgent(
    name="callback_agent",
    model=MODEL_NAME,
    instruction="Use the test_tool to respond to the user. Return the tool's output verbatim.",
    tools=[FunctionTool(func=_mock_tool_func)],
    before_tool_callback=None,  # Placeholder, will be set in the test
    after_tool_callback=None,  # Placeholder, will be set in the test
)
# END: CODE
# LLM_CONTEXT_END


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

    # Re-instantiate the agent here to apply the actual callback functions
    agent_for_test = LlmAgent(
        name="callback_agent",
        model=MODEL_NAME,
        instruction="Use the test_tool to respond to the user. Return the tool's output verbatim.",
        tools=[FunctionTool(func=_mock_tool_func)],
        before_tool_callback=before_callback_func,
        after_tool_callback=after_callback_func,
    )

    # Manually run the agent logic without run_agent_test to have full control over mocking
    with patch(
        "google.adk.models.google_llm.Gemini.generate_content_async"
    ) as mock_generate:

        async def async_response_gen_tool_call():
            # First response: Tool call
            response = types.GenerateContentResponse()
            response.candidates = [
                types.Candidate(
                    content=types.Content(
                        parts=[
                            types.Part(
                                function_call=types.FunctionCall(
                                    name="_mock_tool_func", args={"query": "hello"}
                                )
                            )
                        ],
                        role="model",
                    )
                )
            ]
            yield LlmResponse.create(response)

        async def async_response_gen_final():
            # Second response: Final text
            response = types.GenerateContentResponse()
            response.candidates = [
                types.Candidate(
                    finish_reason="STOP",
                    content=types.Content(
                        parts=[types.Part(text="UNIQUE_TOOL_OUTPUT_FOR_TEST: hello")],
                        role="model",
                    ),
                )
            ]
            yield LlmResponse.create(response)

        # Mock side_effect to return sequential responses
        response_iter = iter(
            [async_response_gen_tool_call(), async_response_gen_final()]
        )
        mock_generate.side_effect = lambda *args, **kwargs: next(response_iter)

        app = App(name=f"test_app_{agent_for_test.name}", root_agent=agent_for_test)
        runner = InMemoryRunner(app=app)

        session = await runner.session_service.create_session(
            app_name=app.name, user_id="test-user", state={}
        )

        final_response = ""
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text="Use the tool with 'hello'")]
            ),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text_parts = [
                    part.text
                    for part in event.content.parts
                    if hasattr(part, "text") and part.text is not None
                ]
                if text_parts:
                    final_response = "".join(text_parts)

        assert before_called
        assert after_called
        assert "UNIQUE_TOOL_OUTPUT_FOR_TEST: hello" in final_response
