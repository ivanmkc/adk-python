from __future__ import annotations
from google.adk.agents import LlmAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a minimal, syntactically correct LlmAgent.

  This function represents the correct implementation (ground truth) for benchmark testing.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent.
  """
  root_agent = LlmAgent(
      name="syntax_agent",
      model=model_name,
      instruction="You are a helpful assistant.",
  )
  return root_agent
