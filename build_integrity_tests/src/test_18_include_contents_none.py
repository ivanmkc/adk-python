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

"""Build integrity test for LlmAgent with include_contents='none'."""

from __future__ import annotations

import pytest

from google.adk.agents import LlmAgent
from build_integrity_tests.src._rigs import MODEL_NAME, run_agent_test


@pytest.mark.asyncio
async def test_include_contents_none_stateless_agent():
  """Tests that LlmAgent with include_contents='none' acts as a stateless agent."""
  agent = LlmAgent(
      name="stateless_agent",
      model=MODEL_NAME,
      instruction="Your name is StatelessBot. You are a stateless agent and do not retain information from previous turns.",
      include_contents="none",
  )

  # First turn: Agent should introduce itself
  response1 = await run_agent_test(agent, "What is your name?")
  assert "StatelessBot" in response1

  # Second turn: Agent should confirm its stateless nature and not recall the specific previous question.
  response2 = await run_agent_test(agent, "Do you remember what I asked you before?")
  assert "stateless" in response2.lower()
  assert "remember" in response2.lower() # It should state that it doesn't remember
  assert "what is your name" not in response2.lower() # It should not recall the specific question
