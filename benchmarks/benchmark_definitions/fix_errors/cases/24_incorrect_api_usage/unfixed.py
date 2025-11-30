from __future__ import annotations
from google.adk.agents import LlmAgent

def create_agent(model_name: str) -> BaseAgent:
    """
    Creates an LlmAgent with incorrect API usage (wrong parameter name).

    This function is designed to represent a broken state (ValidationError) that the LLM needs to fix.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of LlmAgent (if the API usage were corrected).

    Raises:
        ValidationError: Always, due to the incorrect parameter name.
    """
    # Incorrect parameter name 'instructions' instead of 'instruction'
    # This raises ValidationError in LlmAgent constructor (Pydantic model)
    root_agent = LlmAgent(
        name='api_agent',
        model=model_name,
        instructions='You are a helpful assistant.' # Incorrect arg
    )
    return root_agent
