from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent

def create_agent(model_name: str) -> BaseAgent:
    """
    Creates a stateless LlmAgent using `include_contents="none"`.

    This function represents the correct implementation for benchmark testing.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        A stateless instance of LlmAgent.
    """
    agent = LlmAgent(
        name="stateless_agent",
        model=model_name,
        instruction="Your name is StatelessBot. You are a stateless agent and do not retain information from previous turns.",
        include_contents="none",
    )
    return agent
