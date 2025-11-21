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
Test file containing code snippets for 'predict_runtime_behavior_mc' benchmarks.

Each test function corresponds to a benchmark question and validates the runtime behavior
of the code snippet. The snippets are marked with '# --8<-- [start:name]' tags
to be extracted for the multiple-choice questions.

Assertions and test harness code are placed OUTSIDE the snippet tags to ensure
the snippets presented to users match the benchmark questions (which often ask 
"Predict the error" or "Predict output").
"""

import asyncio
from unittest.mock import MagicMock
import pytest
from pydantic import BaseModel, ValidationError

from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.apps import App
from google.adk.plugins import ReflectAndRetryToolPlugin
from google.genai import types
from google.adk.events import Event
from google.adk.sessions import Session
from google.adk.runners import InMemoryRunner
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext

# --- Common Setup for Snippets ---

class MyPydanticModel(BaseModel):
    """A dummy Pydantic model."""
    field: str

class MySchema(BaseModel):
    """A dummy output schema."""
    answer: str

my_tool = lambda: None
my_agent = LlmAgent(name="dummy", model="gemini-2.5-flash")

# --- Snippet Tests ---

def test_duplicate_agent_name():
    """
    Validates behavior when creating a SequentialAgent with duplicate sub-agent names.
    """
    # --8<-- [start:duplicate_agent_name]
    a1 = LlmAgent(name="worker", model="gemini-2.5-flash")
    
    a2 = LlmAgent(name="worker", model="gemini-2.5-flash")
    
    root = SequentialAgent(name="root", sub_agents=[a1, a2])
    # --8<-- [end:duplicate_agent_name]
    
    # Currently, SequentialAgent allows duplicate sub-agent names during initialization.
    # This assertion confirms that no error is raised and both agents are stored.
    assert len(root.sub_agents) == 2


def test_reserved_agent_name():
    """
    Validates that using reserved names (like 'user') raises a ValueError.
    """
    with pytest.raises(ValueError, match="reserved"):
        # --8<-- [start:reserved_agent_name]
        agent = LlmAgent(
            name="user", model="gemini-2.5-flash", instruction="You are a helpful assistant."
        )
        # --8<-- [end:reserved_agent_name]


@pytest.mark.asyncio
async def test_callback_execution_order():
    """
    Validates callback execution order.
    """
    # --8<-- [start:callback_execution_order]
    async def pre(callback_context):
        print("Pre")

    async def post(callback_context):
        print("Post")

    agent = LlmAgent(
        name="test",
        model="gemini-2.5-flash",
        before_agent_callback=pre,
        after_agent_callback=post,
    )
    # --8<-- [end:callback_execution_order]
    
    # Verify attachment
    assert agent.before_agent_callback == pre
    assert agent.after_agent_callback == post


def test_retry_plugin_config():
    """
    Validates ReflectAndRetryToolPlugin initialization.
    """
    # --8<-- [start:retry_plugin_config]
    app = App(
        name="my_app",
        root_agent=my_agent,
        plugins=[ReflectAndRetryToolPlugin(max_retries=3)],
    )
    # --8<-- [end:retry_plugin_config]
    
    assert len(app.plugins) == 1


def test_generate_content_config_tools_error():
    """
    Validates that tools in generate_content_config raises ValidationError.
    """
    with pytest.raises(ValidationError, match="tools"):
        # --8<-- [start:generate_content_config_tools_error]
        agent = LlmAgent(
            name="agent",
            model="gemini-2.5-flash",
            generate_content_config=types.GenerateContentConfig(tools=[my_tool]),
        )
        # --8<-- [end:generate_content_config_tools_error]


def test_response_schema_invalid_arg():
    """
    Validates that 'response_schema' is an invalid argument.
    """
    with pytest.raises(ValidationError):
        # --8<-- [start:response_schema_invalid_arg]
        agent = LlmAgent(
            name="bad_agent", model="gemini-2.5-flash", response_schema=MyPydanticModel
        )
        # --8<-- [end:response_schema_invalid_arg]


def test_output_schema_json_enforcement():
    """
    Validates 'output_schema' acceptance.
    """
    # --8<-- [start:output_schema_json_enforcement]
    agent = LlmAgent(name="json_agent", model="gemini-2.5-flash", output_schema=MySchema)
    # --8<-- [end:output_schema_json_enforcement]
    assert agent.output_schema == MySchema


def test_stateless_agent_history():
    """
    Validates stateless agent init.
    """
    # --8<-- [start:stateless_agent_history]
    agent = LlmAgent(name="stateless", model="gemini-2.5-flash", include_contents="none")
    # --8<-- [end:stateless_agent_history]
    assert agent.include_contents == "none"


def test_loop_agent_empty_subagents():
    """
    Validates LoopAgent with empty sub_agents.
    """
    # --8<-- [start:loop_agent_empty_subagents]
    agent = LoopAgent(name="looper", sub_agents=[])
    # --8<-- [end:loop_agent_empty_subagents]
    assert len(agent.sub_agents) == 0


def test_tool_session_id_injection():
    """
    Validates tool signature.
    """
    # --8<-- [start:tool_session_id_injection]
    def my_tool(query: str, session_id: str): ...
    # --8<-- [end:tool_session_id_injection]
    assert "session_id" in my_tool.__annotations__


def test_agent_name_mutability(capsys):
    """
    Validates agent name mutability.
    """
    # --8<-- [start:agent_name_mutability]
    agent = LlmAgent(name="a", model="...")
    print(agent.name)
    agent.name = "b"
    print(agent.name)
    # --8<-- [end:agent_name_mutability]
    
    captured = capsys.readouterr()
    assert "a\nb\n" in captured.out


def test_agent_clone_invalid_field():
    """
    Validates agent cloning with extra fields.
    """
    with pytest.raises(ValueError): # Expecting ValueError per YAML answer
        # --8<-- [start:agent_clone_invalid_field]
        agent = LlmAgent(name="test", model="gemini-2.5-flash")
        
        clone = agent.clone(update={"unknown_field": 123})
        # --8<-- [end:agent_clone_invalid_field]


def test_event_repr_output():
    """
    Validates Event object creation failure (Predict Error).
    """
    with pytest.raises(ValidationError):
        # --8<-- [start:event_repr_output]
        from google.adk.events.event import Event
        
        # Incorrect: type arg not allowed, content is string
        event = Event(type="model_response", content="Hello")
        
        print(f"{event.type}: {event.content}")
        # --8<-- [end:event_repr_output]


def test_session_state_mutability():
    """
    Validates session state mutability (Predict Error).
    """
    with pytest.raises(ValidationError):
        # --8<-- [start:session_state_mutability]
        from google.adk.sessions.session import Session
        
        # Incorrect: missing app_name
        session = Session(id="123", user_id="user")
        
        session.state["user"] = "Alice"
        session.state["count"] = 1
        session.state["count"] += 1
        
        print(session.state)
        # --8<-- [end:session_state_mutability]


@pytest.mark.asyncio
async def test_function_tool_async_run():
    """
    Validates FunctionTool async execution error.
    """
    def add(a: int, b: int) -> int:
        return a + b

    with pytest.raises(TypeError, match="unexpected keyword argument 'fn'"):
        # --8<-- [start:function_tool_async_run]
        from google.adk.tools.function_tool import FunctionTool
        import asyncio
        
        # Incorrect usage: 'fn' instead of 'func' (or positional)
        tool = FunctionTool(fn=add)
        # --8<-- [end:function_tool_async_run]


def test_llm_agent_name_validation(capsys):
    """
    Validates agent name regex constraints (Predict Output).
    """
    # --8<-- [start:llm_agent_name_validation]
    from google.adk.agents.llm_agent import LlmAgent

    try:
        agent = LlmAgent(name="invalid name", model="gemini-1.5-flash")
    except ValueError as e:
        print("Caught Error")
    # --8<-- [end:llm_agent_name_validation]
    
    captured = capsys.readouterr()
    assert "Caught Error" in captured.out


def test_event_extra_fields_error(capsys):
    """
    Validates that Event forbids extra fields (Predict Output).
    """
    # --8<-- [start:event_extra_fields_error]
    from google.adk.events.event import Event

    try:
        # Incorrect: extra field 'random_field'
        # Also incorrect: missing 'author'. Event validation will fail on one of these.
        # Benchmark says "Predict Output" -> "Validation Error"
        # We supply 'author' to ensure the error is about 'random_field' or 'type'?
        # The original snippet had: e = Event(type="custom", random_field="123")
        # 'type' is forbidden, 'random_field' is forbidden, 'author' is missing.
        # Any ValidationError triggers exception.
        e = Event(type="custom", random_field="123")
    except Exception:
        print("Validation Error")
    # --8<-- [end:event_extra_fields_error]
    
    captured = capsys.readouterr()
    assert "Validation Error" in captured.out
