"""
Benchmark Case 02: An LlmAgent with a simple function tool.

Description:
  This benchmark tests the ability to create an LlmAgent that is equipped with a specific tool.
  The agent, named 'root_agent', must be able to use the provided `basic_tool`.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that:
    - Has access to the tool.
    - Correctly calls the tool when prompted ("Can you use your tool?").
    - Returns a response containing the tool's output ("test").
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
        root_agent,
        "Can you use your tool?",
        mock_llm_response="I used the tool with query 'test'",
    )
    assert "test" in response.lower()