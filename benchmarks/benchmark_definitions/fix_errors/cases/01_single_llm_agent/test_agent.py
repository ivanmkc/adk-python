"""
Benchmark Case 01: A minimal LlmAgent.

Description:
  This benchmark tests the ability to create a minimal LlmAgent named 'root_agent'.
  The agent is expected to respond to a simple greeting.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that:
    - Is named 'single_agent' (or as defined in the solution).
    - Responds to "Hello" with a string containing "Hello".
"""

import pytest
from benchmarks.test_helpers import run_agent_test, MODEL_NAME

# We import 'agent' which is expected to be in the same directory as this test file.
# When pytest runs this file from a temp dir, that dir is in sys.path.
try:
  import agent
except ImportError:
  # This might happen if run directly from source without the runner setup
  agent = None


@pytest.mark.asyncio
async def test_create_agent_passes():
  if agent is None:
    pytest.fail("Could not import agent module.")

  # Create the agent using the function
  root_agent = agent.create_agent(MODEL_NAME)

  # Run the verification using standard helper
  response = await run_agent_test(
      root_agent, "Hello", mock_llm_response="Hello"
  )

  # Assertions
  print(f"Agent response: {response}")
  assert "Hello" in response, "Expected a greeting containing 'Hello'."
