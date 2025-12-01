from __future__ import annotations
from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a SequentialAgent that orchestrates two simple LlmAgents.

  This function represents the correct implementation for benchmark testing.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of SequentialAgent with configured sub-agents.
  """
  agent_one = LlmAgent(
      name="agent_one",
      model=model_name,
      instruction="This is the first agent. Respond with 'one'.",
  )
  agent_two = LlmAgent(
      name="agent_two",
      model=model_name,
      instruction="This is the second agent. Respond with 'two'.",
  )

  root_agent = SequentialAgent(
      name="sequential_coordinator", sub_agents=[agent_one, agent_two]
  )
  return root_agent
