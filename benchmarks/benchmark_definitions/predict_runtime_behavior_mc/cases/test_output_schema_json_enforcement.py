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
from pydantic import BaseModel

def test_output_schema_json_enforcement():
    """
    Validates 'output_schema' acceptance.
    """
    class MySchema(BaseModel):
        answer: str
    # Expected behavior: The LlmAgent is created successfully with the
    # `output_schema` parameter.
    agent = LlmAgent(
        name="json_agent", model="gemini-2.5-flash", output_schema=MySchema
    )
    assert agent.output_schema == MySchema

    # Assert incorrect options:
    # Option A: structured output is supported in LlmAgent.
    # Option B: `output_format='json'` is not required.
    # Option C: MySchema does not need to be converted to a dict.
