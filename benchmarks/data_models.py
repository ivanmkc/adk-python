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

"""Pydantic data models for benchmarks."""

import enum
import abc
from pathlib import Path
from typing import Annotated, Literal, Union, Optional

import pydantic
from pydantic import Field


class BenchmarkType(str, enum.Enum):
  """The type of benchmark."""

  FIX_ERROR = "fix_error"
  API_UNDERSTANDING = "api_understanding"


class ExpectedOutcome(str, enum.Enum):
  """The expected outcome of a benchmark."""

  PASS = "pass"
  FAIL_WITH_ERROR = "fail_with_error"


class BaseBenchmarkCase(pydantic.BaseModel, abc.ABC):
  """Abstract base class for a single benchmark case."""

  benchmark_type: BenchmarkType

  @abc.abstractmethod
  def get_identifier(self) -> str:
    """Returns a unique identifier for the benchmark case."""
    raise NotImplementedError


class FixErrorBenchmarkCase(BaseBenchmarkCase):
  """Represents a single fix_error benchmark case."""

  name: str
  description: str
  benchmark_type: Literal[BenchmarkType.FIX_ERROR] = BenchmarkType.FIX_ERROR
  test_file: Path
  start_line: int
  end_line: int

  def get_identifier(self) -> str:
    return self.name


class StringMatchAnswer(pydantic.BaseModel):
  """Represents an answer that is a string match."""

  answer_template: Literal["StringMatchAnswer"]
  answer: str
  module_path: str


class AnswerTemplate(enum.Enum):
  """The template for the answer."""

  CLASS_DEFINITION = "CLASS_DEFINITION"
  METHOD_DEFINITION = "METHOD_DEFINITION"
  PARAMETER_DEFINITION = "PARAMETER_DEFINITION"
  TYPE_ALIAS_DEFINITION = "TYPE_ALIAS_DEFINITION"
  CODE_BLOCK = "CODE_BLOCK"


class ApiUnderstandingBenchmarkCase(BaseBenchmarkCase):
  """Represents a single API understanding benchmark case (from adk_faq.yaml)."""

  category: str
  question: str
  rationale: str
  benchmark_type: Literal[BenchmarkType.API_UNDERSTANDING] = (
      BenchmarkType.API_UNDERSTANDING
  )
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

  def get_identifier(self) -> str:
    return self.question


BenchmarkCase = Annotated[
    Union[FixErrorBenchmarkCase, ApiUnderstandingBenchmarkCase],
    Field(discriminator="benchmark_type"),
]


class BenchmarkFile(pydantic.BaseModel):
  """Represents an entire benchmark YAML file."""

  benchmarks: list[BenchmarkCase]


class BenchmarkResult(pydantic.BaseModel):
  """Represents the result of a benchmark run."""

  outcome: ExpectedOutcome
  error_type: Optional[str] = None
  error_message: Optional[str] = None
