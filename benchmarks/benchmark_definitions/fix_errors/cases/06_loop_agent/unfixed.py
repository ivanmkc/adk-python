from __future__ import annotations
from google.adk.agents import LlmAgent, LoopAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a buggy LoopAgent with incorrect loop configuration.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of BaseAgent, expected to fail in loop execution.
  """
  raise NotImplementedError("Agent not implemented for unfixed version.")
