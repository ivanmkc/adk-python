from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a buggy LlmAgent for direct InMemoryRunner testing.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of BaseAgent, expected to fail.
  """
  raise NotImplementedError("Agent not implemented for unfixed version.")
