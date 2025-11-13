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
import enum
import re
import sys
from pathlib import Path
from typing import Callable, Union, Literal

import pydantic
import yaml

# --- Pydantic Data Models for adk_faq.yaml ---


class TypeDefAnswer(pydantic.BaseModel):
  """Represents an answer that is a type definition."""

  answer_type: Literal["TypeDefAnswer"]
  name: str
  type: str
  signature: str

# I will need to add other structured answer types here later if needed.
# For now, let's keep it simple.

class FaqItem(pydantic.BaseModel):
  """Represents a single FAQ entry."""

  category: str
  question: str
  rationale: str
  answer: TypeDefAnswer # This will be Union[TypeDefAnswer, ...] later
  file: Path
  line_of_code_start: int
  line_of_code_end: int
  # test_assertion: TestAssertion # This field is removed as answer is now structured

  @pydantic.validator("line_of_code_end")
  def start_must_be_before_end(cls, v, values):
    if "line_of_code_start" in values and v < values["line_of_code_start"]:
      raise ValueError("line_of_code_end must not be before line_of_code_start")
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


def validate_type_def(code_block: str, answer: TypeDefAnswer) -> bool:
  """Validates a TypeDefAnswer against a block of code using regex based on type."""
  pattern = ""
  if answer.type == "class":
    pattern = rf"^\s*class\s+{re.escape(answer.name)}\b"
  elif answer.type == "method" or answer.type == "function":
    pattern = rf"^\s*(?:async\s+)?def\s+{re.escape(answer.name)}\s*\("
  elif answer.type == "parameter":
    pattern = rf"{re.escape(answer.signature)}"
  elif answer.type == "constant":
    pattern = rf"\b{re.escape(answer.name)}\b"
  elif answer.type == "import":
    pattern = rf"^\s*{re.escape(answer.signature)}\b"
  elif answer.type == "environment_variable":
    pattern = rf"\b{re.escape(answer.name)}\b"
  elif answer.type == "field":
    pattern = rf"\b{re.escape(answer.name)}\b"
  elif answer.type == "command":
    pattern = rf"^{re.escape(answer.signature)}\b"
  elif answer.type == "property":
    pattern = rf"^\s*def\s+{re.escape(answer.name)}\b"
  elif answer.type == "type":
    pattern = rf"^{re.escape(answer.name)}:\s*TypeAlias\s*=\s*Union\["
  elif answer.type == "code":
    pattern = rf"{re.escape(answer.signature)}"
  else:
    return False # Unsupported type for now

  if not pattern:
    return False

  if answer.type in ["constant", "environment_variable", "field"]:
    return bool(re.search(pattern, code_block, re.MULTILINE)) and answer.signature in code_block
  else:
    return bool(re.search(pattern, code_block, re.MULTILINE))


# VALIDATORS: dict[AssertionMethod, Callable[[str, str], bool]] = { # This was removed
#     AssertionMethod.CONTAINS: validate_contains,
#     AssertionMethod.REGEX: validate_regex,
# }


def run_validation(faq_file_path: Path) -> bool:
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
    faq_data = FaqFile.parse_obj(data)
  except FileNotFoundError:
    print(f"{FAIL_COLOR}ERROR: File not found: {faq_file_path}{RESET_COLOR}")
    return False
  except (yaml.YAMLError, pydantic.ValidationError) as e:
    print(f"{FAIL_COLOR}ERROR: Failed to parse or validate YAML structure.{RESET_COLOR}")
    print(e)
    return False

  passed_count = 0
  failed_count = 0

  for i, item in enumerate(faq_data.faq):
    result = False
    error_message = ""

    if not item.file.exists():
      error_message = f"File not found: {item.file}"
    else:
      try:
        with open(item.file, "r", encoding="utf-8") as f:
          lines = f.readlines()
        # Adjust for 0-based indexing and inclusive end line
        code_block = "".join(lines[item.line_of_code_start - 1 : item.line_of_code_end])

        # New validation logic based on structured answer
        if isinstance(item.answer, TypeDefAnswer):
            result = validate_type_def(code_block, item.answer)
            if not result:
              error_message = "TypeDefAnswer assertion failed."
        else:
            error_message = f"Unsupported answer type: {type(item.answer)}"

      except IndexError:
        error_message = f"Line numbers are out of bounds for file {item.file}."
      except Exception as e:
        error_message = f"An unexpected error occurred: {e}"

    if result:
      print(
          f"{i+1:02d}: {SUCCESS_COLOR}PASS{RESET_COLOR} - {item.question}"
      )
      passed_count += 1
    else:
      print(
          f"{i+1:02d}: {FAIL_COLOR}FAIL{RESET_COLOR} - {item.question} ({error_message})"
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

  if not run_validation(args.faq_file):
    sys.exit(1)


if __name__ == "__main__":
  main()
