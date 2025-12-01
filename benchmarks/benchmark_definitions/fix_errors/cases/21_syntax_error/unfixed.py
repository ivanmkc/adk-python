from __future__ import annotations
from google.adk.agents import LlmAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a dummy LlmAgent with a simulated syntax error.

  In a real scenario, this function would contain syntactically incorrect Python.
  For this benchmark, it simulates a state that the LLM needs to 'fix' to a valid agent.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent (assuming fixed by the LLM).
  """
  root_agent = LlmAgent(
      name="syntax_agent",
      model=model_name,
      instruction="You are a helpful assistant.",
  )
  return root_agent
