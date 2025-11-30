from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.tools import FunctionTool
from typing import Any, Dict, Optional

async def _mock_tool_func(query: str) -> str:
    return f"UNIQUE_TOOL_OUTPUT_FOR_TEST: {query}"

before_called: list[bool] = []
after_called: list[bool] = []

async def before_callback_func(tool: FunctionTool, args: Dict[str, Any], tool_context: Any) -> Optional[Dict[str, Any]]:
    """Callback executed before a tool call."""
    before_called.append(True)
    return None  # Do not modify tool args

async def after_callback_func(tool: FunctionTool, args: Dict[str, Any], tool_context: Any, tool_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Callback executed after a tool call."""
    after_called.append(True)
    return None  # Do not modify tool response

def create_agent(model_name: str) -> BaseAgent:
    """
    Creates an LlmAgent with `before_tool_callback` and `after_tool_callback`.

    This function represents the correct implementation for benchmark testing.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of LlmAgent with configured tool callbacks.
    """
    root_agent = LlmAgent(
        name="callback_agent",
        model=model_name,
        instruction="Use the test_tool to respond to the user. Return the tool's output verbatim.",
        tools=[FunctionTool(func=_mock_tool_func)],
        before_tool_callback=before_callback_func,
        after_tool_callback=after_callback_func,
    )
    return root_agent
