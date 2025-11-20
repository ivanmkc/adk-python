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

"""Build integrity test for LlmAgent with artifacts."""

from __future__ import annotations

import pytest

from google.adk.agents import LlmAgent
from benchmarks.test_helpers import MODEL_NAME, run_agent_test


@pytest.mark.asyncio
async def test_artifact_usage_in_instruction():
    """Tests that LlmAgent can use artifacts referenced in its instruction."""
    artifact_data = {"my_data": "important information"}

    # BEGIN: CODE
    # BEGIN: CODE
    # END: CODE

    response = await run_agent_test(
        agent, "What is the data?", artifact_data=artifact_data
    )
    assert "important information" in response


@pytest.mark.asyncio
async def test_artifact_creation_and_reference():
    """Tests that an agent can create an artifact and it can be referenced."""
    # This test is more complex as it requires the agent to *create* an artifact
    # which is typically done via a tool or a specific agent capability.
    # For now, we'll focus on the agent *using* an artifact provided to it.
    # A more advanced test would involve a tool that creates an artifact.
    pass
