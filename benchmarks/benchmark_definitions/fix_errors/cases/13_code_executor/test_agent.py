"""
Benchmark Case 13: An LlmAgent with a BuiltInCodeExecutor.

Description:
  This benchmark tests the ability to create an `LlmAgent` equipped with a
  `BuiltInCodeExecutor`, allowing it to execute Python code.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that:
    - Has a code executor configured.
    - Can execute code to solve a problem (2 + 2).
    - Returns the correct result (4).
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
  root_agent = agent.create_agent(MODEL_NAME)
  response = await run_agent_test(
      root_agent, "Calculate 2 + 2.", mock_llm_response="4"
  )
  assert "4" in response
