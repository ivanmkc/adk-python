from __future__ import annotations
from google.adk.agents import LlmAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates an LlmAgent with a correct instruction to respond with "Hello World!".

  This function represents the correct implementation (ground truth) for benchmark testing.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent with the correct logic.
  """
  root_agent = LlmAgent(
      name="logic_agent",
      model=model_name,
      instruction=(
          'You are a helpful assistant. Always respond with "Hello World!".'
      ),
  )
  return root_agent
