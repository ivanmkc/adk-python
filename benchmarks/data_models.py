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

import abc
import enum
from pathlib import Path
from typing import Annotated
from typing import Literal
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

import pydantic
from pydantic import Field

if TYPE_CHECKING:
    from benchmarks.benchmark_runner import ApiUnderstandingRunner
    from benchmarks.benchmark_runner import BaseBenchmarkRunner
    from benchmarks.benchmark_runner import PytestBenchmarkRunner


class BenchmarkType(str, enum.Enum):
    """The type of benchmark."""

    FIX_ERROR = "fix_error"

    API_UNDERSTANDING = "api_understanding"

    MULTIPLE_CHOICE = "multiple_choice"


class CodeSnippetRef(pydantic.BaseModel):
    """Reference to a code snippet in a file."""

    file: str
    section: str


class ExpectedOutcome(str, enum.Enum):
    """The expected outcome of a benchmark."""

    PASS = "pass"

    FAIL_WITH_ERROR = "fail_with_error"


class BaseBenchmarkCase(pydantic.BaseModel, abc.ABC):
    """Abstract base class for a single benchmark case."""

    benchmark_type: BenchmarkType
    code_snippet_ref: Optional[CodeSnippetRef] = None

    @abc.abstractmethod
    def get_identifier(self) -> str:
        """Returns a unique identifier for the benchmark case."""

        raise NotImplementedError

    @property
    @abc.abstractmethod
    def runner(self) -> "BaseBenchmarkRunner":
        """Returns the benchmark runner for this case."""

        raise NotImplementedError


class CodeContext(pydantic.BaseModel):
    """Specifies the code context to be provided to the LLM."""

    file: Path


class FixErrorBenchmarkCase(BaseBenchmarkCase):
    """Represents a single fix_error benchmark case."""

    name: str

    description: str

    benchmark_type: Literal[BenchmarkType.FIX_ERROR] = BenchmarkType.FIX_ERROR

    test_file: Path

    # DEPRECATED: These fields will be replaced by code_context.
    start_line: int | None = None

    end_line: int | None = None

    # NEW FIELDS
    requirements: list[str] | None = None

    code_context: CodeContext | None = None

    def get_identifier(self) -> str:

        return self.name

    @property
    def runner(self) -> "PytestBenchmarkRunner":

        from benchmarks.benchmark_runner import PytestBenchmarkRunner

        return PytestBenchmarkRunner()


class StringMatchAnswer(pydantic.BaseModel):
    """Represents an answer that is a string match."""

    answer_template: Literal["StringMatchAnswer"]

    answer: str

    fully_qualified_class_name: list[str] = pydantic.Field(
        ...,
        description="A list of fully qualified names (FQN) for the relevant class. This should include the module path and the class's name only, not method or parameter names. Example: 'google.adk.agents.llm_agent.LlmAgent'",
    )


class AnswerTemplate(str, enum.Enum):
    """The template for the answer."""

    CLASS_DEFINITION = "class_definition"

    PARAMETER_DEFINITION = "parameter_definition"

    METHOD_DEFINITION = "method_definition"

    TYPE_ALIAS_DEFINITION = "type_alias_definition"

    CODE_BLOCK = "code_block"

    IDENTIFIER = "identifier"


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

    @pydantic.validator("answers", pre=True, each_item=True)
    def anwers_str_to_list(cls, v):
        if isinstance(v, dict) and isinstance(v.get("fully_qualified_class_name"), str):
            v["fully_qualified_class_name"] = [v["fully_qualified_class_name"]]
        return v

    def get_identifier(self) -> str:

        return self.question

    @property
    def runner(self) -> "ApiUnderstandingRunner":

        from benchmarks.benchmark_runner import ApiUnderstandingRunner

        return ApiUnderstandingRunner()


class MultipleChoiceBenchmarkCase(BaseBenchmarkCase):
    """Represents a single multiple choice benchmark case."""

    question: str
    options: dict[str, str]  # e.g., {"A": "Option A", "B": "Option B"}
    correct_answer: str  # e.g., "B"
    explanation: Optional[str] = None

    benchmark_type: Literal[BenchmarkType.MULTIPLE_CHOICE] = (
        BenchmarkType.MULTIPLE_CHOICE
    )

    def get_identifier(self) -> str:
        return self.question[:50] + "..."

    @property
    def runner(self) -> "MultipleChoiceRunner":
        from benchmarks.benchmark_runner import MultipleChoiceRunner

        return MultipleChoiceRunner()


BenchmarkCase = Annotated[
    Union[
        FixErrorBenchmarkCase,
        ApiUnderstandingBenchmarkCase,
        MultipleChoiceBenchmarkCase,
    ],
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

    rationale: str = Field(
        ..., description="Explanation of the thinking process leading to the answer."
    )


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

    fully_qualified_class_name: str = Field(
        description="""The fully qualified name (FQN) for the relevant class. This should


        be the path to the module file itself, including the class's name only, not method or parameter names.





        Examples:


        - Good: 'google.adk.agents.llm_agent.LlmAgent'


        - Bad: 'google.adk.agents.llm_agent.LlmAgent.model' (includes parameter name)


        - Bad: 'google.adk.runners.Runner.run' (includes method name)""",
    )


class MultipleChoiceAnswerOutput(BaseAnswerOutput):
    """The expected output structure for a multiple_choice benchmark."""

    benchmark_type: Literal[BenchmarkType.MULTIPLE_CHOICE] = (
        BenchmarkType.MULTIPLE_CHOICE
    )

    answer: str = Field(
        ...,
        description="The single letter corresponding to the chosen answer (e.g., 'A', 'B', 'C', or 'D').",
    )


AnswerOutput = Annotated[
    Union[
        FixErrorAnswerOutput,
        ApiUnderstandingAnswerOutput,
        MultipleChoiceAnswerOutput,
    ],
    Field(discriminator="benchmark_type"),
]


class GeneratedAnswer(pydantic.BaseModel):
    """
    Represents the structured output from an AnswerGenerator, akin to an
    LLM's function call result.
    """

    output: AnswerOutput


class BenchmarkRunResult(pydantic.BaseModel):
    """Represents the structured result of a single benchmark run."""

    suite: str
    benchmark_name: str
    answer_generator: str
    result: int = Field(
        ..., description="The result of the benchmark run: 1 for pass, 0 for fail."
    )
    answer: str
    rationale: Optional[str] = None
    validation_error: Optional[str] = None
    temp_test_file: Optional[str] = None
    latency: float = 0.0
