from __future__ import annotations
from google.adk.agents import LlmAgent, ParallelAgent, BaseAgent

def create_agent(model_name: str) -> BaseAgent:
    """
    Creates a ParallelAgent that runs two LlmAgents concurrently.

    This function represents the correct implementation for benchmark testing.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of ParallelAgent with configured sub-agents.
    """
    agent_one = LlmAgent(
        name="agent_one",
        model=model_name,
        instruction="Respond with only the text: This is the first parallel agent.",
    )
    agent_two = LlmAgent(
        name="agent_two",
        model=model_name,
        instruction="Respond with only the text: This is the second parallel agent.",
    )

    root_agent = ParallelAgent(
        name="parallel_coordinator", sub_agents=[agent_one, agent_two]
    )
    return root_agent
