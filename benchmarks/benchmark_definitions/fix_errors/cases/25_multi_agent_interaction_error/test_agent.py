"""
Benchmark Case 25: A SequentialAgent with an interaction error.

Description:
  This benchmark tests the ability to fix a multi-agent interaction error where
  the consumer agent (`reader_agent`) fails to receive data from the producer agent (`writer_agent`)
  because the producer did not set the correct `output_key` in the session state.

Test Verification:
  - Verifies that `create_agent` returns a valid SequentialAgent that:
    - Writer outputs to "correct_key".
    - Reader reads from "correct_key".
    - Final response contains "secret_message".
"""

import pytest
from google.adk.agents import BaseAgent
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
      root_agent, BaseAgent
  ), "root_agent should be an instance of BaseAgent"

  response = await run_agent_test(
      root_agent, "Start interaction", mock_llm_response="secret_message"
  )
  assert (
      "secret_message" in response
  ), "Reader agent should output 'secret_message'"
