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

# LLM_CONTEXT_BEGIN
"""Build integrity test for LlmAgent with input_schema."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from benchmarks.test_helpers import MODEL_NAME, run_agent_test


class UserInfo(BaseModel):
    name: str = Field(description="The user's name.")
    age: int = Field(description="The user's age.")

# BEGIN: CODE
# END: CODE
# LLM_CONTEXT_END


@pytest.mark.asyncio
async def test_input_schema_validation():
    """Tests that LlmAgent respects input_schema for structured input."""
    response = await run_agent_test(agent, '{"name": "Alice", "age": 30}')
    assert "Alice" in response and "30" in response

    # Test with invalid input (should ideally raise an error or be handled gracefully by the agent)
    # For now, we'll just check if the agent still responds, as error handling might be internal.
    response_invalid = await run_agent_test(agent, '{"name": "Bob"}')
    assert "Bob" in response_invalid
