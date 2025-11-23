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
"""14: An LlmAgent using an OpenAI model via LiteLlm."""

from __future__ import annotations

import os
import pytest
from google.adk.agents import LlmAgent
from benchmarks.test_helpers import run_agent_test

# Skip this test if the OPENAI_API_KEY is not set.
pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY is not set."
)

# BEGIN: CODE
# END: CODE
# LLM_CONTEXT_END


async def run_test() -> str:
    """Runs the agent and returns the response."""
    return await run_agent_test(root_agent, "Hello")


def assert_test(response: str):
    """Asserts the response is valid."""
    print(f"Agent response: {response}")
    assert "Hello" in response


async def test_agent_with_litellm_openai():
    """Tests that an agent can use an OpenAI model via LiteLlm."""
    response = await run_test()
    assert_test(response)
