"""
Benchmark Case 15: An LlmAgent with an after_model_callback.

Description:
  This benchmark tests the ability to attach an `after_model_callback` to an `LlmAgent`.
  The callback should be executed after the model responds.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that:
    - Responds to a greeting.
    - Triggers the registered `my_callback`, setting a flag in the `agent` module.
"""

import pytest
from benchmarks.test_helpers import run_agent_test, MODEL_NAME

try:
  import agent
except ImportError:
  agent = None


@pytest.mark.asyncio
async def test_create_agent_passes():
  if agent is None:
    pytest.fail("No agent module")

  # Reset the flag in the agent module
  agent.callback_was_called = False

  root_agent = agent.create_agent(MODEL_NAME)
  response = await run_agent_test(
      root_agent, "Hello", mock_llm_response="Hello"
  )

  assert "Hello" in response or "Hi" in response
  assert agent.callback_was_called, "The after_model_callback was not called."
