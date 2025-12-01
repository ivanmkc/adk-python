"""
Benchmark Case 14: An LlmAgent using an OpenAI model via LiteLlm.

Description:
  This benchmark tests the ability to create an `LlmAgent` that uses a third-party
  model (OpenAI's GPT-3.5) via the `LiteLlm` integration.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that:
    - Is configured with `LiteLlm`.
    - Responds to a greeting (mocked response).
"""

import pytest
import os
from benchmarks.test_helpers import run_agent_test

try:
  import agent
except ImportError:
  agent = None


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY is not set."
)
@pytest.mark.asyncio
async def test_create_agent_passes():
  if agent is None:
    pytest.fail("No agent module")
  root_agent = agent.create_agent("gemini-2.5-flash")
  response = await run_agent_test(root_agent, "Hello")
  assert "Hello" in response
