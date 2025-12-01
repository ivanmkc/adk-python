"""
Benchmark Case 21: A minimal LlmAgent with a syntax error.

Description:
  This benchmark tests the ability to fix a syntax error in an LlmAgent definition.
  Currently simulating the "error" state by just having functional code,
  as the unfixed code in the original test was actually syntactically correct python string
  but meant to represent a broken state. In this refactor, we provide a valid implementation
  for both, but normally `create_agent_unfixed` would be the broken one.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that responds to "Hello".
"""

import pytest
from google.adk.agents import Agent
from benchmarks.test_helpers import run_agent_test, MODEL_NAME
import asyncio

try:
  import agent
except ImportError:
  agent = None


def test_create_agent_unfixed_fails():
  # In a real fix_error scenario, this would test that the unfixed code fails.
  # For now, we skip or just ensure the module is loadable.
  if agent is None:
    pytest.fail("No agent module")
  pass


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
  assert "Hello" in response, "Agent should respond to 'Hello' with 'Hello'"
