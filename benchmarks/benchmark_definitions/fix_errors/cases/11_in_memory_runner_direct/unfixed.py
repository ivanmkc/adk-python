from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a simple LlmAgent for direct InMemoryRunner testing.

  Instructions:
      Create an LlmAgent named "runnable_agent" that responds to "Hello, runner."
      with a greeting containing "Hello".

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent.
  """
  raise NotImplementedError("Agent implementation incomplete.")
