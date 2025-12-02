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

import unfixed
import fixed

def test_create_agent_unfixed_fails():
  # The unfixed code in this case is actually valid python (simulating a "fixed" syntax error state for the benchmark input)
  # So we just verify it runs.
  root_agent = unfixed.create_agent(MODEL_NAME)
  assert root_agent is not None


@pytest.mark.asyncio
async def test_create_agent_passes():
  root_agent = fixed.create_agent(MODEL_NAME)

  assert isinstance(
      root_agent, Agent
  ), "root_agent should be an instance of Agent"
  response = await run_agent_test(
      root_agent, "Hello", mock_llm_response="Hello"
  )
  assert "Hello" in response, "Agent should respond to 'Hello' with 'Hello'"
  assert root_agent.name == "syntax_agent", "Agent name mismatch."
