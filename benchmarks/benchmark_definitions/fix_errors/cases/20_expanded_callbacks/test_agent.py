"""
Benchmark Case 20: Build integrity test for LlmAgent with expanded callbacks.

Description:
  This benchmark tests the ability to create an `LlmAgent` with `before_tool_callback`
  and `after_tool_callback` hooks.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that:
    - Executes the tool.
    - Triggers the `before_tool_callback`.
    - Triggers the `after_tool_callback`.
    - Returns the tool's output.
"""

import pytest
from unittest.mock import patch
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from benchmarks.test_helpers import MODEL_NAME

try:
  import agent
except ImportError:
  agent = None


@pytest.mark.asyncio
async def test_create_agent_passes():
  if agent is None:
    pytest.fail("No agent module")

  # Reset callbacks
  agent.before_called = []
  agent.after_called = []

  root_agent = agent.create_agent(MODEL_NAME)

  # Manually run the agent logic with mocks
  with patch(
      "google.adk.models.google_llm.Gemini.generate_content_async"
  ) as mock_generate:

    async def async_response_gen_tool_call():
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

    response_iter = iter(
        [async_response_gen_tool_call(), async_response_gen_final()]
    )
    mock_generate.side_effect = lambda *args, **kwargs: next(response_iter)

    app = App(name=f"test_app_{root_agent.name}", root_agent=root_agent)
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
        text_parts = [p.text for p in event.content.parts if p.text]
        if text_parts:
          final_response = "".join(text_parts)

    assert agent.before_called
    assert agent.after_called
    assert "UNIQUE_TOOL_OUTPUT_FOR_TEST: hello" in final_response
