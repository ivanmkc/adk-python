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
Test file containing code snippets for 'diagnose_setup_errors_mc' benchmarks.
These snippets are intentionally buggy or incomplete to test error diagnosis.
"""

import sys

from google.adk.agents import LlmAgent
from google.adk.agents import LoopAgent
from google.adk.agents import ParallelAgent
from google.adk.agents import SequentialAgent
from google.adk.agents.run_config import RunConfig
from google.adk.apps import App
from google.adk.apps.events_compaction import EventsCompactionConfig
from google.adk.runners import Runner
from google.adk.sessions import ContextCacheConfig
from google.adk.tools import BuiltInCodeExecutor
from google.genai import types
from pydantic import BaseModel
from pydantic import ValidationError
import pytest


# Mock classes/functions for context
def calculate_tax():
    pass


class UserInfo(BaseModel):
    name: str
    age: int


class MyPydanticModel(BaseModel):
    field: str


agent_one = LlmAgent(name="one", model="gemini-2.5-flash")
agent_two = LlmAgent(name="two", model="gemini-2.5-flash")
specialist_agent = LlmAgent(
    name="specialist", model="gemini-2.5-flash", description="Spec"
)
child = LlmAgent(name="child", model="gemini-2.5-flash")
root = LlmAgent(name="root", model="gemini-2.5-flash")
agent = LlmAgent(name="agent", model="gemini-2.5-flash")
my_app = App(name="my_app", root_agent=agent_one)
my_agent = agent_one
other_agent = agent_two
tool = calculate_tax
schema = MyPydanticModel
ThinkingConfig = object  # Dummy
parent = agent_one


def test_missing_model_arg():
    """Snippet: missing model argument in LlmAgent."""
    # Expect: ValidationError because 'model' field is required for LlmAgent.
    with pytest.raises(ValidationError):
        # --8<-- [start:missing_model_arg]
        root_agent = LlmAgent(
            name="my_agent", instruction="You are a helpful assistant."
        )
        # --8<-- [end:missing_model_arg]


def test_raw_function_tool():
    """Snippet: passing raw function instead of FunctionTool."""
    # Expect: ValueError or similar because raw functions must be wrapped in FunctionTool.
    # ADK validation logic checks this.
    with pytest.raises(Exception):
        # --8<-- [start:raw_function_tool]
        root_agent = LlmAgent(
            name="tax_agent", model="gemini-2.5-flash", tools=[calculate_tax]
        )
        # --8<-- [end:raw_function_tool]


def test_sequential_agent_tools():
    """Snippet: using tools param instead of sub_agents in SequentialAgent."""
    # Expect: Since SequentialAgent doesn't take 'tools' as init arg for agents, but it might not fail loudly if it just accepts kwargs?
    # Actually, SequentialAgent inherits from BaseAgent which takes tools. But SequentialAgent needs sub_agents.
    # The snippet uses 'tools=[agent_one, agent_two]'. Agents are not Tools.
    # This will likely fail type checking or runtime validation when tools are processed.
    with pytest.raises(Exception):
        # --8<-- [start:sequential_agent_tools]
        root_agent = SequentialAgent(name="sequence", tools=[agent_one, agent_two])
        # --8<-- [end:sequential_agent_tools]


def test_code_executor_in_tools():
    """Snippet: passing BuiltInCodeExecutor in tools list."""
    # Expect: BuiltInCodeExecutor should be passed to code_executor param, not tools.
    # Passing it in tools might raise error because it's not a BaseTool subclass or doesn't fit the tool schema expectation if strict.
    # Or it might be an error because code_execution tools are handled specially.
    with pytest.raises(Exception):
        # --8<-- [start:code_executor_in_tools]
        root_agent = LlmAgent(
            name="coder", model="gemini-2.5-flash", tools=[BuiltInCodeExecutor()]
        )
        # --8<-- [end:code_executor_in_tools]


def test_delegation_in_tools():
    """Snippet: passing agent in tools list for delegation."""
    # Expect: Agents passed in 'tools' is invalid; they should be in sub_agents/delegates.
    # This will raise an error because LlmAgent expects BaseTool instances in tools.
    with pytest.raises(Exception):
        # --8<-- [start:delegation_in_tools]
        root_agent = LlmAgent(
            name="manager", model="gemini-2.5-flash", tools=[specialist_agent]
        )
        # --8<-- [end:delegation_in_tools]


def test_invalid_multi_agent_class():
    """Snippet: using non-existent MultiAgent class."""
    # Expect: NameError because MultiAgent is not imported/defined.
    with pytest.raises(NameError):
        # --8<-- [start:invalid_multi_agent_class]
        root_agent = MultiAgent(name="parallel_run", agents=[agent_a, agent_b])
        # --8<-- [end:invalid_multi_agent_class]


def test_input_schema_instance():
    """Snippet: passing instance instead of class to input_schema."""
    # Expect: input_schema expects a Type[BaseModel] or dict, not an instance.
    # This usually raises TypeError or Pydantic validation error.
    with pytest.raises(Exception):
        # --8<-- [start:input_schema_instance]
        class UserInfo(BaseModel):
            name: str
            age: int

        root_agent = LlmAgent(
            name="form_filler", model="gemini-2.5-flash", input_schema=UserInfo()
        )
        # --8<-- [end:input_schema_instance]


def test_output_schema_params():
    """Snippet: using incorrect parameters for output schema."""
    # Expect: 'schema' is not a valid argument for LlmAgent (it uses output_schema).
    with pytest.raises(Exception):
        # --8<-- [start:output_schema_params]
        root_agent = LlmAgent(
            name="json_agent",
            model="gemini-2.5-flash",
            output_format="json",
            schema=MyPydanticModel,
        )
        # --8<-- [end:output_schema_params]


def test_invalid_agent_name_hyphen():
    """Snippet: agent name with hyphen."""
    # Expect: ValueError because agent names must be valid python identifiers (no hyphens).
    with pytest.raises(ValueError):
        # --8<-- [start:invalid_agent_name_hyphen]
        agent = LlmAgent(name="my-agent", model="gemini-1.5-pro")
        # --8<-- [end:invalid_agent_name_hyphen]


def test_gen_config_sys_instr():
    """Snippet: system_instruction in generate_content_config."""
    # Expect: ValueError because system_instruction must be set via agent arg, not config.
    with pytest.raises(ValueError):
        # --8<-- [start:gen_config_sys_instr]
        agent = LlmAgent(
            name="agent",
            model="gemini-1.5-pro",
            generate_content_config=types.GenerateContentConfig(
                system_instruction="Hi"
            ),
        )
        # --8<-- [end:gen_config_sys_instr]


def test_gen_config_tools():
    """Snippet: tools in generate_content_config."""
    # Expect: ValueError because tools must be set via agent arg.
    with pytest.raises(ValueError):
        # --8<-- [start:gen_config_tools]
        agent = LlmAgent(
            name="agent",
            model="gemini-1.5-pro",
            generate_content_config=types.GenerateContentConfig(tools=[tool]),
        )
        # --8<-- [end:gen_config_tools]


def test_gen_config_response_schema():
    """Snippet: response_schema in generate_content_config."""
    # Expect: ValueError because response_schema must be set via output_schema arg.
    with pytest.raises(ValueError):
        # --8<-- [start:gen_config_response_schema]
        agent = LlmAgent(
            name="agent",
            model="gemini-1.5-pro",
            generate_content_config=types.GenerateContentConfig(response_schema=schema),
        )
        # --8<-- [end:gen_config_response_schema]


def test_runner_app_and_agent():
    """Snippet: initializing Runner with both app and agent."""
    # Expect: ValueError because arguments are mutually exclusive.
    with pytest.raises(ValueError):
        # --8<-- [start:runner_app_and_agent]
        runner = Runner(app=my_app, agent=my_agent)
        # --8<-- [end:runner_app_and_agent]


def test_runner_no_app_no_name():
    """Snippet: initializing Runner with agent but no app_name."""
    # Expect: ValueError because app_name is required when app is not provided.
    with pytest.raises(ValueError):
        # --8<-- [start:runner_no_app_no_name]
        runner = Runner(agent=my_agent)
        # --8<-- [end:runner_no_app_no_name]


def test_invalid_app_name():
    """Snippet: invalid app name with spaces."""
    # Expect: ValueError because app name must be valid identifier.
    with pytest.raises(ValueError):
        # --8<-- [start:invalid_app_name]
        app = App(name="my app", root_agent=agent)
        # --8<-- [end:invalid_app_name]


def test_clone_parent_agent():
    """Snippet: attempting to update parent_agent in clone."""
    # Expect: ValueError because parent_agent is read-only/managed by system.
    with pytest.raises(ValueError):
        # --8<-- [start:clone_parent_agent]
        new_agent = agent.clone(update={"parent_agent": other_agent})
        # --8<-- [end:clone_parent_agent]


def test_clone_unknown_field():
    """Snippet: attempting to update unknown field in clone."""
    # Expect: ValueError because 'random_field' does not exist.
    with pytest.raises(ValueError):
        # --8<-- [start:clone_unknown_field]
        new_agent = agent.clone(update={"random_field": 123})
        # --8<-- [end:clone_unknown_field]


def test_sequential_empty_subagents():
    """Snippet: SequentialAgent with no sub_agents."""
    # Expect: This might NOT raise an error at init, but is functionally useless.
    # However, the question implies checking for 'missing required argument sub_agents' or similar if it's required.
    # If it's not required, this test passes without raises.
    # Let's assume for the benchmark context it might be considered an issue, but if code runs fine, we just call it.
    # --8<-- [start:sequential_empty_subagents]
    agent = SequentialAgent(name="seq")
    # --8<-- [end:sequential_empty_subagents]


def test_shared_agent_ownership():
    """Snippet: adding same agent to multiple parents."""
    # Expect: ValueError because agent cannot be reused/assigned multiple parents.
    with pytest.raises(ValueError):
        # --8<-- [start:shared_agent_ownership]
        parent1 = SequentialAgent(name="p1", sub_agents=[child])

        parent2 = SequentialAgent(name="p2", sub_agents=[child])
        # --8<-- [end:shared_agent_ownership]


def test_gen_config_thinking():
    """Snippet: thinking_config in generate_content_config."""
    # Expect: ValueError because thinking_config must be set via planner arg.
    with pytest.raises(ValueError):
        # --8<-- [start:gen_config_thinking]
        agent = LlmAgent(
            name="a",
            model="m",
            generate_content_config=types.GenerateContentConfig(thinking_config=...),
        )
        # --8<-- [end:gen_config_thinking]


def test_run_config_max_calls_overflow():
    """Snippet: max_llm_calls overflow."""
    # Expect: ValueError because value exceeds allowed max.
    with pytest.raises(ValueError):
        # --8<-- [start:run_config_max_calls_overflow]
        config = RunConfig(max_llm_calls=sys.maxsize)
        # --8<-- [end:run_config_max_calls_overflow]


def test_loop_agent_missing_max_iter():
    """Snippet: LoopAgent without max_iterations."""
    # Expect: This likely does NOT raise an error (defaults to infinite), but is a potential "gotcha".
    # We just run it.
    # --8<-- [start:loop_agent_missing_max_iter]
    agent = LoopAgent(name="loop", sub_agents=[child])
    # --8<-- [end:loop_agent_missing_max_iter]


def test_set_parent_agent_init():
    """Snippet: setting parent_agent in init."""
    # Expect: TypeError or ValueError because parent_agent is init=False.
    with pytest.raises((TypeError, ValueError)):
        # --8<-- [start:set_parent_agent_init]
        agent = LlmAgent(name="child", parent_agent=parent)
        # --8<-- [end:set_parent_agent_init]


def test_cache_ttl_string():
    """Snippet: ContextCacheConfig ttl as string."""
    # Expect: ValidationError because ttl must be int.
    with pytest.raises(ValidationError):
        # --8<-- [start:cache_ttl_string]
        config = ContextCacheConfig(ttl="3600s")
        # --8<-- [end:cache_ttl_string]


def test_app_extra_args():
    """Snippet: App with invalid extra args."""
    # Expect: ValidationError because 'agents' is not a valid field.
    with pytest.raises(ValidationError):
        # --8<-- [start:app_extra_args]
        app = App(name="app", root_agent=root, agents=[root])
        # --8<-- [end:app_extra_args]


def test_compaction_overlap_negative():
    """Snippet: EventsCompactionConfig overlap_size negative."""
    # Expect: ValidationError.
    with pytest.raises(ValidationError):
        # --8<-- [start:compaction_overlap_negative]
        EventsCompactionConfig(overlap_size=-1)
        # --8<-- [end:compaction_overlap_negative]


def test_compaction_interval_zero():
    """Snippet: EventsCompactionConfig compaction_interval zero."""
    # Expect: ValidationError.
    with pytest.raises(ValidationError):
        # --8<-- [start:compaction_interval_zero]
        EventsCompactionConfig(compaction_interval=0)
        # --8<-- [end:compaction_interval_zero]


def test_compaction_summarizer_string():
    """Snippet: EventsCompactionConfig summarizer as string."""
    # Expect: ValidationError.
    with pytest.raises(ValidationError):
        # --8<-- [start:compaction_summarizer_string]
        EventsCompactionConfig(summarizer="string")
        # --8<-- [end:compaction_summarizer_string]


def test_parallel_max_workers_string():
    """Snippet: ParallelAgent max_workers as string."""
    # Expect: ValidationError.
    with pytest.raises(ValidationError):
        # --8<-- [start:parallel_max_workers_string]
        agent = ParallelAgent(name="p", max_workers="10")
        # --8<-- [end:parallel_max_workers_string]
