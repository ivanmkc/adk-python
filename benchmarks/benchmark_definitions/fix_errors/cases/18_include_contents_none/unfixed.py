from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a buggy LlmAgent with incorrect `include_contents` configuration.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of BaseAgent, expected to fail in stateless behavior.
  """
  raise NotImplementedError("Agent not implemented for unfixed version.")
