"""
Benchmark Case 23: A minimal LlmAgent with a missing import.

Description:
  This benchmark tests the ability to fix a `NameError` caused by a missing import
  of `LlmAgent`.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent.
"""

import pytest
from google.adk.agents import Agent
from benchmarks.test_helpers import run_agent_test, MODEL_NAME
import asyncio

try:
  import agent
except ImportError:
  agent = None


@pytest.mark.asyncio
async def test_create_agent_passes():
  if agent is None:
    pytest.fail("No agent module")
  root_agent = agent.create_agent(MODEL_NAME)

  assert isinstance(
      root_agent, Agent
  ), "root_agent should be an instance of Agent"
  response = await run_agent_test(
      root_agent, "Hello", mock_llm_response="Hello"
  )
  assert "Hello" in response
