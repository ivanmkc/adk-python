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
  Creates an App instance that includes a basic plugin and a root LlmAgent.

  This function represents the correct implementation for benchmark testing.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of App with a configured plugin.
  """
  root_agent = LlmAgent(
      name="app_agent",
      model=model_name,
      instruction="You are an agent within an App.",
  )

  app = App(
      name="my_app",
      root_agent=root_agent,
      plugins=[SimplePlugin()],
  )
  return app
