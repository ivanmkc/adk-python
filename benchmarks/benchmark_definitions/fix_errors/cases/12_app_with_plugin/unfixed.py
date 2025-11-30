from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.apps import App
from google.adk.plugins import BasePlugin

class SimplePlugin(BasePlugin):
    """A simple plugin that adds a prefix to the response."""

    def __init__(self) -> None:
        super().__init__(name="simple_plugin")

    async def after_agent_callback(self, **kwargs) -> None:
        # This is a simplified example. A real plugin would modify the event.
        print("SimplePlugin: after_agent_callback")

def create_agent(model_name: str) -> BaseAgent:
    """
    Creates a buggy App instance with incorrect plugin configuration.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of BaseAgent, expected to fail in plugin integration.
    """
    raise NotImplementedError("Agent not implemented for unfixed version.")
