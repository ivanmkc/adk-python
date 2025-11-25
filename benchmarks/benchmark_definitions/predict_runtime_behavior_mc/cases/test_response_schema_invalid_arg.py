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
from pydantic import BaseModel, ValidationError

# LLM_CONTEXT_BEGIN
def code_under_test():
    class MyPydanticModel(BaseModel):
        field: str
    LlmAgent(
        name="bad_agent", model="gemini-2.5-flash", response_schema=MyPydanticModel
    )
# LLM_CONTEXT_END

def test_response_schema_invalid_arg():
    """
    Validates that 'response_schema' is an invalid argument.
    """
    # Expected behavior: A ValidationError is raised because `response_schema`
    # is not a valid argument for `LlmAgent`.
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        code_under_test()