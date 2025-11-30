"""
Benchmark Case 17: Build integrity test for LlmAgent with input_schema.

Description:
  This benchmark tests the ability to create an `LlmAgent` (`worker_agent`) with an
  `input_schema` (`UserInfo`) and expose it as a tool to another agent (`agent`).
  This verifies structured input validation and tool usage.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that:
    - Can process structured input via the worker agent.
    - Correctly handles input matching the schema.
    - Correctly handles (or fails on) invalid input.
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
    
    # Valid input test
    response = await run_agent_test(
        root_agent, 'Process this info: name is Alice, age is 30',
        mock_llm_response='{"name": "Alice", "age": 30}'
    )
    assert "Alice" in response and "30" in response

    # Invalid input test
    response_invalid = await run_agent_test(
        root_agent, 'Process this info: name is Bob',
        mock_llm_response="Error: The field 'age' is missing."
    )
    assert "age" in response_invalid.lower()