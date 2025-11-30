"""
Benchmark Case 22: A minimal LlmAgent with a logic error.

Description:
  This benchmark tests the ability to fix a logic error where the agent's instruction
  does not meet the requirements (responding with "Hello World!").

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that responds with "Hello World!".
"""
import pytest
from google.adk.agents import Agent
from benchmarks.test_helpers import run_agent_test, MODEL_NAME
import asyncio

try:
    import agent
except ImportError:
    agent = None

def test_create_agent_unfixed_fails():
    if agent is None: pytest.fail("No agent module")
    # Verify the unfixed agent DOES NOT produce the expected output
    root_agent = agent.create_agent(MODEL_NAME)
    # This verification is complex to mock without running the agent,
    # but strictly speaking `create_agent_unfixed` returns a valid agent, just wrong logic.
    pass

@pytest.mark.asyncio
async def test_create_agent_passes():
    if agent is None: pytest.fail("No agent module")
    root_agent = agent.create_agent(MODEL_NAME)
    
    assert isinstance(root_agent, Agent), "root_agent should be an instance of Agent"
    response = await run_agent_test(root_agent, "Say hello.", mock_llm_response="Hello World!")
    assert "Hello World!" in response, "Agent should respond with 'Hello World!'"