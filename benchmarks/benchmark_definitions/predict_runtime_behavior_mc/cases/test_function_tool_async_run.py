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
from google.adk.tools.function_tool import FunctionTool

def test_function_tool_async_run():
    """
    Validates FunctionTool initialization error.
    """
    def add(a: int, b: int) -> int:
        return a + b
    # Expected behavior: A TypeError is raised because `fn` is an unexpected
    # keyword argument.
    with pytest.raises(TypeError, match="unexpected keyword argument 'fn'"):
        FunctionTool(fn=add)

    # Assert incorrect options:
    # Option A, B, D: A TypeError is raised, so these are incorrect.
