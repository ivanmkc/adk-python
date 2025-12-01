from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a minimal LlmAgent.

  This function represents the correct implementation for benchmark testing.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent.
  """
  root_agent = LlmAgent(
      name="single_agent",
      model=model_name,
      instruction="You are a helpful assistant.",
  )
  return root_agent
