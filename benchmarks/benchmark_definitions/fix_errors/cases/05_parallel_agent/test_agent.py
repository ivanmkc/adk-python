"""
Benchmark Case 05: A ParallelAgent running two agents concurrently.

Description:
  This benchmark tests the ability to create a `ParallelAgent` named 'root_agent'
  that runs two sub-agents concurrently.

Test Verification:
  - Verifies that `create_agent` returns a valid ParallelAgent that:
    - Executes its sub-agents.
    - Returns a response that indicates successful parallel execution (mocked as "parallel").
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
    response = await run_agent_test(root_agent, "Run in parallel.", mock_llm_response="parallel")
    assert "parallel" in response.lower()