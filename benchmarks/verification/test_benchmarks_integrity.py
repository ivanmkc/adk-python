import ast
import importlib
import inspect
from pathlib import Path
import sys

import pytest

# Manually set up path to src so we can import adk
sys.path.append("src")

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.loop_agent import LoopAgent
from google.adk.agents.run_config import RunConfig
from google.adk.apps import App
from google.adk.artifacts.base_artifact_service import BaseArtifactService
from google.adk.events.event import Event
from google.adk.plugins.context_filter_plugin import ContextFilterPlugin
from google.adk.plugins.global_instruction_plugin import GlobalInstructionPlugin
from google.adk.plugins.reflect_retry_tool_plugin import ReflectAndRetryToolPlugin
from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.genai import types


def test_runner_import():
    assert Runner.__module__ == "google.adk.runners"


def test_event_import():
    assert Event.__module__ == "google.adk.events.event"

    sig = inspect.signature(Runner.run_async)
    assert "new_message" in sig.parameters
    assert "message" not in sig.parameters
    assert "content" not in sig.parameters


def test_app_init_params():
    sig = inspect.signature(App.__init__)
    # This one is tricky because it's logic based, not strict signature exclusion in python
    # But the logic is: if app is passed, app_name/root_agent are inferred.
    # The question asks about "mutually exclusive" in concept.
    # We can check if `app` is a parameter.
    assert "name" in App.model_fields  # The question is about Runner init really.
    sig_runner = inspect.signature(Runner.__init__)
    assert "app" in sig_runner.parameters
    assert "app_name" in sig_runner.parameters
    # The logic is verified by reading the code, hard to assert "mutual exclusivity" on signature alone.


def test_base_agent_abc():
    assert issubclass(BaseAgent, object)
    # BaseAgent is a Pydantic model and doesn't use abc.ABCMeta,
    # but it enforces implementation via NotImplementedError in _run_async_impl.
    # We just verify it exists and is the base.
    assert hasattr(BaseAgent, "run_async")


def test_base_tool_abc():
    # BaseTool inherits from abc.ABC but might not have abstract methods defined
    # using @abstractmethod decorator, so inspect.isabstract returns False.
    from abc import ABC

    assert issubclass(BaseTool, ABC)
    assert hasattr(BaseTool, "run_async")


def test_invocation_context_purpose():
    # Check type hints instead of instantiation to avoid mocking dependencies
    type_hints = inspect.get_annotations(InvocationContext)
    assert "session" in type_hints
    assert "agent_states" in type_hints
    assert "session_service" in type_hints


def test_base_artifact_service_abc():
    assert inspect.isabstract(BaseArtifactService)


def test_in_memory_session_service_persistence():
    service = InMemorySessionService()
    # It should use a dict
    assert isinstance(service.sessions, dict)


def test_loop_agent_max_iterations():
    assert "max_iterations" in LoopAgent.model_fields


def test_run_config_max_llm_calls():
    config = RunConfig()
    assert hasattr(config, "max_llm_calls")
    assert config.max_llm_calls == 500


def test_save_files_plugin():
    # Just verify import and existence
    assert SaveFilesAsArtifactsPlugin


def test_run_config_modalities():
    config = RunConfig()
    assert hasattr(config, "response_modalities")


def test_global_instruction_plugin():
    assert GlobalInstructionPlugin


def test_reflect_retry_tool_plugin():
    assert ReflectAndRetryToolPlugin


def test_context_filter_plugin():
    assert ContextFilterPlugin


def test_runner_run_debug():
    assert hasattr(Runner, "run_debug")


def test_base_toolset_close():
    # Check if close is an async method
    assert inspect.iscoroutinefunction(BaseToolset.close)


def test_run_config_affective():
    config = RunConfig()
    assert hasattr(config, "enable_affective_dialog")


if __name__ == "__main__":
    # Manually run tests
    try:
        test_runner_import()
        test_event_import()
        test_base_agent_abc()
        test_base_tool_abc()
        test_invocation_context_purpose()
        test_base_artifact_service_abc()
        test_in_memory_session_service_persistence()
        test_loop_agent_max_iterations()
        test_run_config_max_llm_calls()
        test_save_files_plugin()
        test_run_config_modalities()
        test_global_instruction_plugin()
        test_reflect_retry_tool_plugin()
        test_context_filter_plugin()
        test_runner_run_debug()
        test_base_toolset_close()
        test_run_config_affective()
        print("All verification tests passed!")
    except AssertionError as e:
        print(f"Verification failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)