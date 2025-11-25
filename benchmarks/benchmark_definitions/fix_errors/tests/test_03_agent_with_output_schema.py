# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""03: An LlmAgent that uses output_schema to enforce JSON output."""
from __future__ import annotations

import json
import pytest
from pydantic import BaseModel, Field
from benchmarks.test_helpers import MODEL_NAME, run_agent_test

# LLM_CONTEXT_BEGIN
from google.adk.agents import LlmAgent

class BasicOutputSchema(BaseModel):
    """A basic Pydantic model for testing output_schema."""

    field_one: str = Field(description="The first field.")
    field_two: int = Field(description="The second field.")

# BEGIN: CODE
root_agent = LlmAgent(
    name="output_schema_agent",
    model=MODEL_NAME,
    instruction="Output a JSON object with two fields: 'field_one' and 'field_two'.",
    output_schema=BasicOutputSchema,
)
# END: CODE
# LLM_CONTEXT_END

async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "Generate the JSON.")

def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    try:
        data = json.loads(response)
        assert "field_one" in data
        assert "field_two" in data
    except json.JSONDecodeError:
        pytest.fail("The response was not valid JSON.")

async def test_agent_with_output_schema():
    """Tests that an agent can produce a valid JSON output based on a schema."""
    response = await run_test()
    assert_test(response)
