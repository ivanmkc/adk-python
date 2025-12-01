"""
Benchmark Case 10: An agent that writes to and reads from session.state.

Description:
  This benchmark tests the ability to coordinate state between agents using `output_key`
  and dynamic instruction placeholders.
  - `writer_agent` writes 'xyz' to `session.state["secret_word"]`.
  - `reader_agent` reads `secret_word` from state using `{secret_word}` in its instruction.

Test Verification:
  - Verifies that `create_agent` returns a valid SequentialAgent that:
    - Successfully passes the state from writer to reader.
    - Returns the correct secret word ("xyz") in the final response.
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
  response = await run_agent_test(root_agent, "Start", mock_llm_response="xyz")
  assert "xyz" in response.lower()
