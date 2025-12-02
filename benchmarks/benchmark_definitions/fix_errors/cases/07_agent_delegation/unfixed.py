from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a root LlmAgent that delegates a task to a specialist sub-agent.

  Instructions:
      Create a "delegator_agent" that delegates to a "specialist_agent" when needed.
      The specialist_agent should be instructed to respond with "specialist ok".

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent capable of delegation.
  """
  raise NotImplementedError("Agent implementation incomplete.")
