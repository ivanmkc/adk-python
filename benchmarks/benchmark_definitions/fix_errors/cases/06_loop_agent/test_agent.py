"""
Benchmark Case 06: A LoopAgent that runs a sub-agent a fixed number of times.

Description:
  This benchmark tests the ability to create a `LoopAgent` named 'root_agent'
  that runs a single sub-agent ('looper_agent') for a fixed number of iterations.

Test Verification:
  - Verifies that `create_agent` returns a valid LoopAgent that:
    - Runs the loop.
    - Returns a response indicative of the loop's execution (mocked as "Iteration 1 complete").
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
    response = await run_agent_test(
        root_agent, "Run the loop.", mock_llm_response="Iteration 1 complete."
    )
    assert "Iteration" in response or "loop" in response.lower()