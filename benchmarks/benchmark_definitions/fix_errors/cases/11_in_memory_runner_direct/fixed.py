from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a simple LlmAgent for direct InMemoryRunner testing.

  This function represents the correct implementation for benchmark testing.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent.
  """
  root_agent = LlmAgent(
      name="runnable_agent",
      model=model_name,
      instruction="You are a runnable agent.",
  )
  return root_agent
