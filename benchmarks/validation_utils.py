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

"""Utilities for validating generated answers against templates."""

import re
import enum
from typing import Any, Callable, Coroutine, Union

import pydantic
from benchmarks.data_models import AnswerTemplate


# --- Custom Exceptions ---


class ValidationError(Exception):
  """Base class for validation errors."""


class TemplateMismatchError(ValidationError):
  """Raised when an answer does not match its template."""


# --- Template Definitions ---


class TemplateInfo(pydantic.BaseModel):
  """Model for storing information about an answer template."""

  regex: str
  description: str
  examples: list[str]


TEMPLATES = {
    AnswerTemplate.CLASS_DEFINITION: TemplateInfo(
        regex=r"^\s*class\s+\w+(\(.*\))?:\s*$",
        description="A Python class definition.",
        examples=[
            "class MyClass:",
            "class MyClass(object):",
            "class MyClass(BaseClass, Mixin):",
        ],
    ),
    AnswerTemplate.PARAMETER_DEFINITION: TemplateInfo(
        regex=r"^\s*\w+:\s*\S+.*$",
        description="A Python parameter definition (e.g., 'my_param: str').",
        examples=[
            "my_param: str",
            "my_param: Optional[int] = None",
            "my_param: list[str]",
        ],
    ),
    AnswerTemplate.METHOD_DEFINITION: TemplateInfo(
        regex=(
            r"^(?:\s*@.*\n)*\s*(async\s+)?def\s+\w+\(.*\n?(?:.*\n)*\s*\)(?:\s*->\s*.*)?:\s*$"
        ),
        description="A Python method definition.",
        examples=[
            "def my_method(self):",
            "async def my_method(self, arg1: str):",
            "def my_method(self, *args, **kwargs):",
            "async def my_method(\
    self,\n    arg1: str,\n) -> str:",
        ],
    ),
    AnswerTemplate.TYPE_ALIAS_DEFINITION: TemplateInfo(
        regex=r"^\s*\w+:\s*TypeAlias\s*=\s*[\s\S]*$",
        description="A Python TypeAlias definition.",
        examples=[
            "MyType: TypeAlias = Union[str, int]",
            "AnotherType: TypeAlias = Callable[[str], None]",
        ],
    ),
    AnswerTemplate.CODE_BLOCK: TemplateInfo(
        regex=r"^[\s\S]*$",  # Matches any code block
        description="A Python code block.",
        examples=[
            "if x > 0:\n    return True",
            "for i in range(10):\n    print(i)",
        ],

    ),
}


def validate_answer_against_template(answer: str, template: AnswerTemplate):
  """Validates that the answer matches the regex for the given template."""
  template_info = TEMPLATES.get(template)
  if not template_info:
    raise TemplateMismatchError(f"No template defined for '{template.value}'")

  regex = template_info.regex
  if not re.match(regex, answer):
    raise TemplateMismatchError(
        f"Answer '{answer}' does not match the format for template"
        f" '{template.value}'. Expected format: {template_info.description}"
    )
