from __future__ import annotations
from google.adk.agents import LlmAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates an LlmAgent with a logic error in its instruction.

  The instruction is insufficient for the agent to meet a specific requirement.
  This simulates a scenario where the LLM needs to fix the agent's behavior.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent with a logic flaw.
  """
  # Logic error: Missing the required instruction to always respond with "Hello World!"
  root_agent = LlmAgent(
      name="logic_agent",
      model=model_name,
      instruction="You are a helpful assistant.",  # Wrong instruction for the test
  )
  return root_agent
