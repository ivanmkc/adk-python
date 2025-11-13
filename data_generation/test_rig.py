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

"""A test rig to validate the adk_faq.yaml file against the codebase."""

import argparse
import asyncio
import enum
import re
import sys
from pathlib import Path
from typing import Literal

import pydantic
import yaml

# --- Custom Exceptions ---


class ValidationError(Exception):
  """Base class for validation errors."""


class TemplateMismatchError(ValidationError):
  """Raised when an answer does not match its template."""


class StringMatchError(ValidationError):
  """Raised when the generated answer does not match the code block."""


class FileAccessError(ValidationError):
  """Raised when a file cannot be accessed."""


class LineNumberError(ValidationError):
  """Raised when line numbers are out of bounds."""


# --- Template Definitions ---


class AnswerTemplate(str, enum.Enum):
  """Enum for the different types of answer templates."""

  CLASS_DEFINITION = "CLASS_DEFINITION"
  PARAMETER_DEFINITION = "PARAMETER_DEFINITION"
  METHOD_DEFINITION = "METHOD_DEFINITION"


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
            r"^\s*(async\s+)?def\s+\w+\(.*\n?(?:.*\n)*\s*\)(?:\s*->\s*.*)?:\s*$"
        ),
        description="A Python method definition.",
        examples=[
            "def my_method(self):",
            "async def my_method(self, arg1: str):",
            "def my_method(self, *args, **kwargs):",
            "async def my_method(\\n    self,\\n    arg1: str,\\n) -> str:",
        ],
    ),
}


# --- Pydantic Data Models for adk_faq.yaml ---


class StringMatchAnswer(pydantic.BaseModel):
  """Represents an answer that is a string match."""

  answer_template: Literal["StringMatchAnswer"]
  answer: str
  module_path: str


class FaqItem(pydantic.BaseModel):
  """Represents a single FAQ entry."""

  category: str
  question: str
  rationale: str
  template: AnswerTemplate
  answers: list[StringMatchAnswer]
  file: Path
  line_of_code_start: int
  line_of_code_end: int

  @pydantic.validator("line_of_code_end")
  def start_must_be_before_end(cls, v, values):
    if "line_of_code_start" in values and v < values["line_of_code_start"]:
      raise ValueError(
          "line_of_code_end must not be before line_of_code_start"
      )
    return v


class FaqFile(pydantic.BaseModel):
  """Represents the entire adk_faq.yaml file."""

  commit_hash: str
  faq: list[FaqItem]


# --- Validator Logic ---

SUCCESS_COLOR = "\033[92m"
FAIL_COLOR = "\033[91m"
RESET_COLOR = "\033[0m"


def _normalize_whitespace(text: str) -> str:
  """Collapses all whitespace into single spaces."""
  return " ".join(text.split())


def validate_module_path(module_path: str, file_path: Path):
  """Validates that the module_path correctly corresponds to the file_path."""
  # Strip 'src/' prefix and '.py' suffix, then replace '/' with '.'
  expected_module_path = (
      str(file_path).removeprefix("src/").removesuffix(".py").replace("/", ".")
  )
  if module_path != expected_module_path:
    raise ValidationError(
        f"Module path '{module_path}' does not match the file path"
        f" '{file_path}'. Expected '{expected_module_path}'."
    )


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


def validate_string_match(generated_answer: str, expected_code_snippet: str):
  """Validates that the generated answer exactly matches the expected code snippet after normalizing whitespace."""
  normalized_generated = _normalize_whitespace(generated_answer)
  normalized_expected = _normalize_whitespace(expected_code_snippet)
  if normalized_generated != normalized_expected:
    raise StringMatchError(
        "Generated answer does not exactly match code block (ignoring"
        " whitespace). Generated:"
        f" '{normalized_generated}', Expected: '{normalized_expected}'"
    )


async def run_validation(faq_file_path: Path) -> bool:
  """Loads, parses, and validates the FAQ file against the codebase.

  Args:
    faq_file_path: The path to the adk_faq.yaml file.

  Returns:
    True if all validations pass, False otherwise.
  """
  print(f"--- Running validation for {faq_file_path} ---")
  try:
    with open(faq_file_path, "r", encoding="utf-8") as f:
      data = yaml.safe_load(f)
    faq_data = FaqFile.model_validate(data)
  except FileNotFoundError:
    print(f"{FAIL_COLOR}ERROR: File not found: {faq_file_path}{RESET_COLOR}")
    return False
  except (yaml.YAMLError, pydantic.ValidationError) as e:
    print(
        f"{FAIL_COLOR}ERROR: Failed to parse or validate YAML"
        f" structure.{RESET_COLOR}"
    )
    print(e)
    return False

  passed_count = 0
  failed_count = 0

  for i, item in enumerate(faq_data.faq):
    any_answer_passed = False
    all_errors = []

    try:
      # Resolve the file path relative to the repository root
      repo_root = (
          Path(__file__).parent.parent
      )  # Go up from data_generation/test_rig.py to repo root
      full_file_path = repo_root / item.file

      if not full_file_path.exists():
        raise FileAccessError(f"File not found: {full_file_path}")

      with open(full_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

      code_block = "".join(
          lines[item.line_of_code_start - 1 : item.line_of_code_end]
      )
      docstring_start = code_block.find('"""')
      if docstring_start != -1:
        code_block = code_block[:docstring_start]
      code_block = code_block.strip()

      # Iterate through all possible answers. If any of them pass, the item is considered valid.
      for answer_obj in item.answers:
        try:
          validate_answer_against_template(answer_obj.answer, item.template)
          validate_module_path(answer_obj.module_path, item.file)
          validate_string_match(answer_obj.answer, code_block)
          any_answer_passed = True
          break  # Found a passing answer, no need to check others
        except ValidationError as e:
          all_errors.append(
              f"  - Answer '{_normalize_whitespace(answer_obj.answer)}'"
              f" failed: {e}"
          )

    except (IndexError, FileAccessError) as e:
      all_errors.append(str(e))
    except Exception as e:
      all_errors.append(f"An unexpected error occurred: {e}")

    if any_answer_passed:
      print(f"{i+1:02d}: {SUCCESS_COLOR}PASS{RESET_COLOR} - {item.question}")
      passed_count += 1
    else:
      error_message = "\n".join(all_errors)
      print(
          f"{i+1:02d}: {FAIL_COLOR}FAIL{RESET_COLOR} - {item.question}\n{error_message}"
      )
      failed_count += 1

  print("\n--- Validation Summary ---")
  print(f"Total checks: {len(faq_data.faq)}")
  print(f"{SUCCESS_COLOR}Passed: {passed_count}{RESET_COLOR}")
  print(f"{FAIL_COLOR}Failed: {failed_count}{RESET_COLOR}")
  return failed_count == 0


def main():
  """Main entry point for the script."""
  parser = argparse.ArgumentParser(
      description="Validate the adk_faq.yaml file against the codebase."
  )
  parser.add_argument(
      "faq_file",
      type=Path,
      help="Path to the adk_faq.yaml file.",
  )
  args = parser.parse_args()

  if not asyncio.run(run_validation(args.faq_file)):
    sys.exit(1)


if __name__ == "__main__":
  main()