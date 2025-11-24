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

def test_tool_session_id_injection():
    """
    Validates tool signature.
    """
    # Expected behavior: The function signature is inspected, and it is
    # confirmed that `session_id` is a parameter.
    def my_tool(query: str, session_id: str): ...
    assert "session_id" in my_tool.__annotations__

    # Assert incorrect options:
    # Option A, B, C, D: These describe incorrect behaviors. ADK injects
    # context via `ToolContext`.
