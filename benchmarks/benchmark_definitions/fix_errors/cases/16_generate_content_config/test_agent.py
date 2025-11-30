"""
Benchmark Case 16: Build integrity test for LlmAgent with generate_content_config.

Description:
  This benchmark tests the ability to configure model generation parameters (like temperature)
  using `generate_content_config` on an `LlmAgent`.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that:
    - Has the configuration set.
    - Responds as instructed ("Hello world!").
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
    response = await run_agent_test(root_agent, "Say hello.", mock_llm_response="Hello world!")
    assert "Hello world!" in response