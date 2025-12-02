from __future__ import annotations

from google.adk.agents import LlmAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a minimal LlmAgent.

  Instructions:
      Create an LlmAgent named "syntax_agent" that responds to greetings.
      Ensure the code is syntactically correct.

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
