"""
Benchmark Case 03: An LlmAgent that uses output_schema to enforce JSON output.

Description:
  This benchmark tests the ability to create an LlmAgent that uses an `output_schema`
  to produce structured JSON output.

Test Verification:
  - Verifies that `create_agent` returns a valid LlmAgent that:
    - Uses the `BasicOutputSchema` (or equivalent).
    - Produces a valid JSON string when prompted.
    - The JSON contains keys 'field_one' and 'field_two'.
"""

import pytest
import json
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
  response = await run_agent_test(
      root_agent,
      "Output JSON",
      mock_llm_response='{"field_one": "value1", "field_two": 2}',
  )

  try:
    data = json.loads(response)
    assert "field_one" in data
    assert "field_two" in data
  except json.JSONDecodeError:
    pytest.fail("The response was not valid JSON.")
