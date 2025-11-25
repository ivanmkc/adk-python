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

import pytest
from google.adk.agents import LlmAgent

# LLM_CONTEXT_BEGIN
def code_under_test():
    async def pre(callback_context):
        print("Pre")

    async def post(callback_context):
        print("Post")

    agent = LlmAgent(
        name="test",
        model="gemini-2.5-flash",
        before_agent_callback=pre,
        after_agent_callback=post,
    )
    return agent, pre, post
# LLM_CONTEXT_END

@pytest.mark.asyncio
async def test_callback_execution_order():
    """
    Validates callback execution order.
    """
    # Expected behavior: The `before_agent_callback` runs before the agent
    # execution, and the `after_agent_callback` runs after.
    
    agent, pre, post = code_under_test()
    
    # This test only validates that the callbacks are attached correctly.
    # The actual execution order is tested in the `fix_errors` benchmark.
    assert agent.before_agent_callback == pre
    assert agent.after_agent_callback == post