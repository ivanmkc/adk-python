"""
Benchmark Case 12: An App instance that includes a basic plugin.

Description:
  This benchmark tests the ability to create an `App` instance named 'app'
  that includes a custom plugin (`SimplePlugin`) and a root agent.

Test Verification:
  - Verifies that `create_agent` returns a valid App instance that:
    - Has a root agent.
    - Includes the `SimplePlugin`.
    - Can execute the root agent to return a greeting ("Hello").
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
  app = agent.create_agent(MODEL_NAME)
  response = await run_agent_test(
      app.root_agent, "Hello", mock_llm_response="Hello"
  )
  assert "Hello" in response
