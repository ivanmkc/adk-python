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
from typing import Annotated, Any, Literal, Union, Optional, Type, Self, TYPE_CHECKING

import pydantic
from pydantic import Field

# Import BenchmarkRunner under a TYPE_CHECKING block to avoid circular dependency
if TYPE_CHECKING:
  from benchmarks.benchmark_runner import BenchmarkRunner


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

  @abc.abstractmethod
  def get_runner_class(self) -> Type["BenchmarkRunner[Self]"]:
    """Returns the BenchmarkRunner class responsible for this case type."""
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

  def get_runner_class(self) -> Type["BenchmarkRunner"]:
    """Returns the PytestBenchmarkRunner for fix_error cases."""
    from benchmarks.benchmark_runner import PytestBenchmarkRunner

    return PytestBenchmarkRunner


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

  @pydantic.field_validator("line_of_code_end")
  @classmethod
  def start_must_be_before_end(cls, v: int, info: pydantic.ValidationInfo) -> int:
    if "line_of_code_start" in info.data and v < info.data["line_of_code_start"]:
      raise ValueError(
          "line_of_code_end must not be before line_of_code_start"
      )
    return v

  def get_identifier(self) -> str:
    return self.question

  def get_runner_class(self) -> Type["BenchmarkRunner"]:
    """Returns the ApiUnderstandingRunner for api_understanding cases."""
    from benchmarks.benchmark_runner import ApiUnderstandingRunner

    return ApiUnderstandingRunner


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


# --- Structured Answer Output Models ---


class BaseAnswerOutput(pydantic.BaseModel, abc.ABC):
  """A base model for the structured output of an AnswerGenerator."""

  pass


class FixErrorAnswerOutput(BaseAnswerOutput):
  """The expected output structure for a fix_error benchmark."""

  benchmark_type: Literal[BenchmarkType.FIX_ERROR] = BenchmarkType.FIX_ERROR
  code: str = Field(
      ...,
      description="The complete, corrected Python code snippet to be injected into the test file.",
  )


class ApiUnderstandingAnswerOutput(BaseAnswerOutput):
  """The expected output structure for an api_understanding benchmark."""

  benchmark_type: Literal[BenchmarkType.API_UNDERSTANDING] = (
      BenchmarkType.API_UNDERSTANDING
  )
  code: str = Field(
      ...,
      description="The Python code snippet that answers the question, conforming to the required template.",
  )
  module_path: str = Field(
      ...,
      description="The expected Python module path where this code would be found, e.g., 'google.adk.agents.llm_agent'.",
  )


AnswerOutput = Annotated[
    Union[FixErrorAnswerOutput, ApiUnderstandingAnswerOutput],
    Field(discriminator="benchmark_type"),
]


class GeneratedAnswer(pydantic.BaseModel):
  """
  Represents the structured output from an AnswerGenerator, akin to an
  LLM's function call result.
  """

  output: AnswerOutput
