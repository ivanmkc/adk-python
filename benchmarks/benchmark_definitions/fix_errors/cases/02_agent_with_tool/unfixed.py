from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.tools import FunctionTool

def basic_tool(query: str) -> str:
    """A simple tool that returns a fixed string."""
    return f"The tool received the query: {query}"

def create_agent(model_name: str) -> BaseAgent:
    """
    Creates a buggy LlmAgent with a missing or incorrect tool configuration.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of BaseAgent, expected to fail in tool usage.
    """
    raise NotImplementedError("Agent not implemented for unfixed version.")