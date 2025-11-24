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

def test_agent_name_mutability(capsys):
    """
    Validates agent name mutability.
    """
    # Expected behavior: The agent's name is mutable and can be changed after
    # initialization. The output should be "a" then "b".
    agent = LlmAgent(name="a", model="...")
    print(agent.name)
    agent.name = "b"
    print(agent.name)
    captured = capsys.readouterr()
    assert "a\nb\n" in captured.out

    # Assert incorrect options:
    # Option A: No ValidationError is raised.
    # Option B: The name is updated, not ignored.
    # Option C: No error is raised, the name is not protected.
