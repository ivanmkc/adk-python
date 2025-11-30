from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent

def create_agent(model_name: str) -> BaseAgent:
    """
    Creates an LlmAgent that utilizes artifact data in its instructions.

    This function represents the correct implementation for benchmark testing.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of LlmAgent capable of using artifact data.
    """
    agent = LlmAgent(
        name="artifact_agent",
        model=model_name,
        instruction="You are an assistant that uses provided data. The data is: {artifact.my_data}",
    )
    return agent
