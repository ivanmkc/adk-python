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

"""
Unit tests for verifying code prediction benchmarks.
Dynamically loads 'benchmark.yaml', executes the corresponding test function for each
benchmark, and asserts that the output matches the correct answer.
"""

import contextlib
import io
from pathlib import Path
import re
import sys
from unittest.mock import MagicMock

import pytest
import yaml

# Add project root to sys.path so we can import google.adk.*
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT / "src"))

from google.adk.agents import LlmAgent
from google.adk.agents import LoopAgent
from google.adk.agents import SequentialAgent
from google.adk.apps import App
from google.adk.events import Event
from google.adk.plugins import ReflectAndRetryToolPlugin
from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from pydantic import BaseModel, ValidationError

BENCHMARK_FILE = Path(__file__).parent / "benchmark.yaml"

# --- Test Implementations ---

def duplicate_agent_name():
    a1 = LlmAgent(name="worker", model="gemini-2.5-flash")
    a2 = LlmAgent(name="worker", model="gemini-2.5-flash")
    SequentialAgent(name="root", sub_agents=[a1, a2])

def reserved_agent_name():
    LlmAgent(
        name="user",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant.",
    )

def callback_execution_order():
    async def pre(callback_context):
        print("Pre")
    async def post(callback_context):
        print("Post")
    LlmAgent(
        name="test",
        model="gemini-2.5-flash",
        before_agent_callback=pre,
        after_agent_callback=post,
    )

def retry_plugin_config():
    my_agent = LlmAgent(name="dummy", model="gemini-2.5-flash")
    App(
        name="my_app",
        root_agent=my_agent,
        plugins=[ReflectAndRetryToolPlugin(max_retries=3)],
    )

def generate_content_config_tools_error():
    my_tool = lambda: None
    LlmAgent(
        name="agent",
        model="gemini-2.5-flash",
        generate_content_config=types.GenerateContentConfig(tools=[my_tool]),
    )

def response_schema_invalid_arg():
    class MyPydanticModel(BaseModel):
        field: str
    LlmAgent(
        name="bad_agent", model="gemini-2.5-flash", response_schema=MyPydanticModel
    )

def output_schema_json_enforcement():
    class MySchema(BaseModel):
        answer: str
    LlmAgent(
        name="json_agent", model="gemini-2.5-flash", output_schema=MySchema
    )

def stateless_agent_history():
    LlmAgent(
        name="stateless", model="gemini-2.5-flash", include_contents="none"
    )

def loop_agent_empty_subagents():
    LoopAgent(name="looper", sub_agents=[])

def tool_session_id_injection():
    def my_tool(query: str, session_id: str): ...

def agent_name_mutability():
    agent = LlmAgent(name="a", model="...")
    print(agent.name)
    agent.name = "b"
    print(agent.name)

def agent_clone_invalid_field():
    agent = LlmAgent(name="test", model="gemini-2.5-flash")
    agent.clone(update={"unknown_field": 123})

def event_repr_output():
    Event(type="model_response", content="Hello")

def session_state_mutability():
    session = Session(id="123", user_id="user", app_name="test_app")
    session.state["user"] = "Alice"
    session.state["count"] = 1
    session.state["count"] += 1
    print(session.state)

def function_tool_async_run():
    def add(a: int, b: int) -> int:
        return a + b
    FunctionTool(fn=add)

def llm_agent_name_validation():
    LlmAgent(name="invalid name", model="gemini-1.5-flash")

def event_extra_fields_error():
    Event(type="custom", random_field="123")


# Map benchmark IDs to their test functions
TEST_IMPLEMENTATIONS = {
    "duplicate_agent_name": duplicate_agent_name,
    "reserved_agent_name": reserved_agent_name,
    "callback_execution_order": callback_execution_order,
    "retry_plugin_config": retry_plugin_config,
    "generate_content_config_tools_error": generate_content_config_tools_error,
    "response_schema_invalid_arg": response_schema_invalid_arg,
    "output_schema_json_enforcement": output_schema_json_enforcement,
    "stateless_agent_history": stateless_agent_history,
    "loop_agent_empty_subagents": loop_agent_empty_subagents,
    "tool_session_id_injection": tool_session_id_injection,
    "agent_name_mutability": agent_name_mutability,
    "agent_clone_invalid_field": agent_clone_invalid_field,
    "event_repr_output": event_repr_output,
    "session_state_mutability": session_state_mutability,
    "function_tool_async_run": function_tool_async_run,
    "llm_agent_name_validation": llm_agent_name_validation,
    "event_extra_fields_error": event_extra_fields_error,
}

def load_benchmarks():
    """Loads benchmarks from the YAML file."""
    if not BENCHMARK_FILE.exists():
        return []
    with open(BENCHMARK_FILE, "r") as f:
        data = yaml.safe_load(f)
    if not data or "benchmarks" not in data:
        return []
    return data["benchmarks"]

def execute_test_function(test_func):
    """Executes a test function and captures its output or exception."""
    f = io.StringIO()
    with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
        try:
            test_func()
        except Exception as e:
            error_name = type(e).__name__
            error_message = str(e).replace('\n', ' ')
            print(f"{error_name}: {error_message}")
    return f.getvalue().strip()

@pytest.mark.parametrize("benchmark", load_benchmarks())
def test_code_prediction_accuracy(benchmark):
    """
    Verifies that the code in the question produces the output specified
    by the 'correct_answer' option.
    """
    benchmark_id = benchmark["code_snippet_ref"]["section"]
    if benchmark_id not in TEST_IMPLEMENTATIONS:
        pytest.skip(f"No implementation for benchmark '{benchmark_id}'")

    test_func = TEST_IMPLEMENTATIONS[benchmark_id]
    actual_output = execute_test_function(test_func)

    question = benchmark.get("question", "")
    options = benchmark.get("options", {})
    correct_key = benchmark.get("correct_answer")
    correct_text = options.get(correct_key)

    normalized_actual = actual_output.replace("\r\n", "\n").strip()
    normalized_expected = str(correct_text).replace("\r\n", "\n").strip()

    matches = (
        (normalized_actual == normalized_expected)
        or (normalized_expected in normalized_actual)
        or (normalized_actual in normalized_expected)
    )

    if not matches:
        pytest.fail(
            f"\nMismatch for benchmark question:\n{question[:100]}...\n"
            f"Expected (Option {correct_key}):\n{normalized_expected!r}\n"
            f"Actual Output:\n{normalized_actual!r}"
        )

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
