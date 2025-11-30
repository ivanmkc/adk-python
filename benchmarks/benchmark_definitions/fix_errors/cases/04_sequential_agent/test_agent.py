"""
Benchmark Case 04: A SequentialAgent orchestrating two simple agents.

Description:
  This benchmark tests the ability to create a `SequentialAgent` named 'root_agent'
  that orchestrates two sub-agents ('agent_one' and 'agent_two') in a fixed order.

Test Verification:
  - Verifies that `create_agent` returns a valid SequentialAgent that:
    - Runs the sequence of agents.
    - Returns the final response from the last agent in the chain ("two").
"""
import pytest
from benchmarks.test_helpers import run_agent_test, MODEL_NAME

try:
    import agent
except ImportError:
    agent = None

@pytest.mark.asyncio
async def test_create_agent_passes():
    if agent is None: pytest.fail("No agent module")
    root_agent = agent.create_agent(MODEL_NAME)
    response = await run_agent_test(root_agent, "Run the sequence.", mock_llm_response="two")
    assert "two" in response.lower()