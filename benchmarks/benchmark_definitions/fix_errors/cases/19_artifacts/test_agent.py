"""
Benchmark Case 19: Build integrity test for LlmAgent with artifacts.

Description:
  This benchmark tests the ability to create an `LlmAgent` that can reference
  artifacts (e.g., `{artifact.my_data}`) in its instructions.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that:
    - Can access the data provided in the artifact.
    - Returns the content of the artifact in its response.
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

  artifact_data = {"my_data": "important information"}
  response = await run_agent_test(
      root_agent,
      "What is the data?",
      artifact_data=artifact_data,
      mock_llm_response="important information",
  )
  assert "important information" in response
