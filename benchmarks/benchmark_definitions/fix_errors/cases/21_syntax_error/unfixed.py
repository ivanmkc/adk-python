from __future__ import annotations

from google.adk.agents import BaseAgent, LlmAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a minimal LlmAgent.

  Instructions:
      Create an LlmAgent named "syntax_agent" that responds to greetings.
      Ensure the code is syntactically correct.

      Requirements:
      - The agent should be a valid LlmAgent instance.
      - The agent should respond to the greeting 'Hello' with a response containing 'Hello'.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent.
  """
  return LlmAgent(
      name="syntax_agent",
      model=model_name,
      instruction="You are a helpful assistant.",
  )
