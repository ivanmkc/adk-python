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

"""Unit tests for the test_rig.py script."""

import pytest

from data_generation.test_rig import AnswerTemplate, validate_answer_against_template


@pytest.mark.parametrize(
    "template, valid_answers",
    [
        (
            AnswerTemplate.CLASS_DEFINITION,
            [
                "class MyClass:",
                "class MyClass(object):",
                "class MyClass(BaseClass, Mixin):",
                "  class MyClass:",
            ],
        ),
        (
            AnswerTemplate.PARAMETER_DEFINITION,
            [
                "my_param: str",
                "my_param: Optional[int] = None",
                "  my_param: list[str]",
            ],
        ),
        (
            AnswerTemplate.METHOD_DEFINITION,
            [
                "def my_method(self):",
                "async def my_method(self, arg1: str):",
                "  def my_method(self, *args, **kwargs):",
            ],
        ),
    ],
)
def test_validate_answer_against_template_valid(template, valid_answers):
  """Tests that valid answers match the template's regex."""
  for answer in valid_answers:
    assert validate_answer_against_template(answer, template)


@pytest.mark.parametrize(
    "template, invalid_answers",
    [
        (
            AnswerTemplate.CLASS_DEFINITION,
            [
                "def my_function():",
                "classMyClass:",
                "class MyClass :",
            ],
        ),
        (
            AnswerTemplate.PARAMETER_DEFINITION,
            [
                "my_param str",
                "my_param: ",
                ": str",
            ],
        ),
        (
            AnswerTemplate.METHOD_DEFINITION,
            [
                "class MyClass:",
                "defmy_method():",
                "def my_method() :",
            ],
        ),
    ],
)
def test_validate_answer_against_template_invalid(template, invalid_answers):
  """Tests that invalid answers do not match the template's regex."""
  for answer in invalid_answers:
    assert not validate_answer_against_template(answer, template)
