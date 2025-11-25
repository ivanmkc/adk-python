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

from google.adk.agents import LlmAgent

# LLM_CONTEXT_BEGIN
def code_under_test():
    agent = LlmAgent(
        name="stateless", model="gemini-2.5-flash", include_contents="none"
    )
    return agent
# LLM_CONTEXT_END

def test_stateless_agent_history():
    """
    Validates stateless agent init.
    """
    # Expected behavior: The LlmAgent is created successfully with
    # `include_contents` set to "none".
    agent = code_under_test()
    assert agent.include_contents == "none"