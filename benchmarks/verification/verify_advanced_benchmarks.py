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
Verification script for advanced_adk_usage_benchmarks.yaml.
This script verifies that the API surface, classes, and signatures assumed by the
benchmark questions actually exist and behave as expected in the codebase.
"""

import ast
import sys
import inspect
import importlib
from pathlib import Path

# Ensure src is in path to import adk
# Assuming this script is run from project root or benchmarks/verification/
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root / "src"))

from google.adk.runners import Runner
from google.adk.events.event import Event
from google.adk.apps import App
from google.adk.agents.base_agent import BaseAgent
from google.adk.tools.base_tool import BaseTool
from google.adk.agents.invocation_context import InvocationContext
from google.adk.artifacts.base_artifact_service import BaseArtifactService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.agents.loop_agent import LoopAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.run_config import RunConfig
from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin
from google.adk.plugins.global_instruction_plugin import GlobalInstructionPlugin
from google.adk.plugins.reflect_retry_tool_plugin import ReflectAndRetryToolPlugin
from google.adk.plugins.context_filter_plugin import ContextFilterPlugin
from google.adk.tools.base_toolset import BaseToolset
from google.genai import types
from google.adk.auth.credential_manager import CredentialManager
from google.adk.cli.cli_tools_click import cli_api_server, cli_deploy_cloud_run
from google.adk.evaluation.eval_case import EvalCase, IntermediateData


def test_runner_import():
    assert Runner.__module__ == "google.adk.runners"

def test_event_import():
    assert Event.__module__ == "google.adk.events.event"

def test_runner_run_async_params():
    sig = inspect.signature(Runner.run_async)
    assert "new_message" in sig.parameters
    assert "message" not in sig.parameters
    assert "content" not in sig.parameters

def test_app_init_params():
    # App is a Pydantic model, so we check model_fields
    assert "name" in App.model_fields
    # Runner is a class, we can check init signature
    sig_runner = inspect.signature(Runner.__init__)
    assert "app" in sig_runner.parameters
    assert "app_name" in sig_runner.parameters

def test_base_agent_abc():
    assert issubclass(BaseAgent, object)
    # BaseAgent is a Pydantic model and doesn't use abc.ABCMeta, 
    # but it enforces implementation via NotImplementedError in _run_async_impl.
    assert hasattr(BaseAgent, "run_async")

def test_base_tool_abc():
    # BaseTool inherits from abc.ABC
    from abc import ABC
    assert issubclass(BaseTool, ABC)
    assert hasattr(BaseTool, "run_async")

def test_invocation_context_purpose():
    # Check type hints instead of instantiation
    type_hints = inspect.get_annotations(InvocationContext)
    assert "session" in type_hints
    assert "agent_states" in type_hints
    assert "session_service" in type_hints

def test_base_artifact_service_abc():
    assert inspect.isabstract(BaseArtifactService)

def test_in_memory_session_service_persistence():
    service = InMemorySessionService()
    # It should use a dict called 'sessions'
    assert isinstance(service.sessions, dict)

def test_loop_agent_max_iterations():
    assert "max_iterations" in LoopAgent.model_fields

def test_run_config_max_llm_calls():
    config = RunConfig()
    assert hasattr(config, "max_llm_calls")
    assert config.max_llm_calls == 500

def test_save_files_plugin():
    assert SaveFilesAsArtifactsPlugin

def test_run_config_modalities():
    config = RunConfig()
    assert hasattr(config, "response_modalities")

def test_global_instruction_plugin():
    assert GlobalInstructionPlugin

def test_reflect_retry_tool_plugin():
    # Ensure correct class name
    assert ReflectAndRetryToolPlugin

def test_context_filter_plugin():
    assert ContextFilterPlugin

def test_runner_run_debug():
    assert hasattr(Runner, "run_debug")

def test_base_toolset_close():
    assert inspect.iscoroutinefunction(BaseToolset.close)

def test_run_config_affective():
    config = RunConfig()
    assert hasattr(config, "enable_affective_dialog")

def test_credential_manager_exists():
    assert CredentialManager

def test_cli_trace_flag():
    # Check if --trace_to_cloud is a param for cli_api_server
    params = cli_api_server.params
    trace_param = next((p for p in params if p.name == "trace_to_cloud"), None)
    assert trace_param is not None
    assert trace_param.is_flag

def test_deploy_service_name_flag():
    params = cli_deploy_cloud_run.params
    service_name_param = next((p for p in params if p.name == "service_name"), None)
    assert service_name_param is not None
    assert "--service_name" in service_name_param.opts

def test_multimodal_part_blob():
    # GenAI types.Part should accept inline_data
    sig = inspect.signature(types.Part.__init__)
    assert "inline_data" in sig.parameters

def test_on_tool_error_callback():
    # Check LlmAgent has on_tool_error_callback
    assert "on_tool_error_callback" in LlmAgent.model_fields

def test_eval_case_xor_constraint():
    # Verify EvalCase has logic to enforce conversation XOR conversation_scenario
    # We can try to instantiate it with both and expect error, or inspect the validator
    # The validator is named 'ensure_conversation_xor_conversation_scenario'
    assert hasattr(EvalCase, "ensure_conversation_xor_conversation_scenario")

def test_intermediate_data_structure():
    # Verify IntermediateData fields
    type_hints = inspect.get_annotations(IntermediateData)
    assert "tool_uses" in type_hints
    assert "tool_responses" in type_hints
    assert "intermediate_responses" in type_hints

# --- Negative Test Cases (Verifying distractors are incorrect) ---

def test_negative_runner_import():
    # Option A in Q1: "from google.adk.factory import Runner" -> Should be invalid.
    try:
        import google.adk.factory
        assert False, "google.adk.factory should not exist"
    except ImportError:
        pass
    
    # Option C: google.adk.core
    try:
        import google.adk.core
        assert not hasattr(google.adk.core, "Runner")
    except ImportError:
        pass

def test_negative_app_init():
    # Option B in Q4: App(application=...)
    # We verify this raises a ValidationError (or TypeError due to extra='forbid')
    from pydantic import ValidationError
    try:
        # App requires name and root_agent, passing 'application' should fail
        # We use a dummy agent to satisfy required fields
        dummy_agent = BaseAgent(name="dummy", sub_agents=[]) 
        App(name="test", root_agent=dummy_agent, application="something")
        assert False, "App(application=...) should have failed"
    except ValidationError as e:
        # Expect "Extra inputs are not permitted"
        assert "application" in str(e) or "Extra inputs" in str(e)

def test_negative_run_config():
    # Option C in Q26: llm_call_limit
    config = RunConfig()
    assert not hasattr(config, "llm_call_limit")

def test_negative_reflect_plugin():
    # Option C in Q30: ReflectRetryToolPlugin
    # We verify that the module does not export a class with this EXACT name
    # or if it does, it's deprecated/not the primary one. 
    # Actually, we just check if we can import it.
    try:
        from google.adk.plugins.reflect_retry_tool_plugin import ReflectRetryToolPlugin
        # If it exists, we should check if it's the recommended one or if the question implies otherwise.
        # But based on previous steps, it likely doesn't exist.
        assert False, "ReflectRetryToolPlugin should not exist (or is not the correct answer)"
    except ImportError:
        pass # This is expected

def test_negative_credential_manager():
    # Option A in Q35: AuthService
    # Check if google.adk.auth.credential_manager exports AuthService
    import google.adk.auth.credential_manager as cm
    assert not hasattr(cm, "AuthService")


if __name__ == "__main__":
    print(f"Running verification script from: {__file__}")
    # Manually run all test functions
    current_module = sys.modules[__name__]
    failed = False
    for name, func in inspect.getmembers(current_module, inspect.isfunction):
        if name.startswith("test_"):
            try:
                func()
                # print(f". {name} passed")
            except Exception as e:
                print(f"F {name} failed: {e}")
                import traceback
                traceback.print_exc()
                failed = True
    
    if failed:
        sys.exit(1)
    else:
        print("All verification tests passed!")
