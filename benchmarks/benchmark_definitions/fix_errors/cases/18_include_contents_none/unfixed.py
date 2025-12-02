from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a stateless LlmAgent using `include_contents="none"`.

  Instructions:
      Create an LlmAgent named "stateless_agent" (aka StatelessBot) that is stateless.
      It should not retain conversation history (set `include_contents="none"`).

      Requirements:
      - The agent's name should be 'StatelessBot'.
      - The agent should be initialized with `include_contents='none'`.
      - The agent's instruction should explain that it is a stateless bot.
      - The final solution must be assigned to a variable named `agent`.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      A stateless instance of LlmAgent.
  """
  raise NotImplementedError("Agent implementation incomplete.")
