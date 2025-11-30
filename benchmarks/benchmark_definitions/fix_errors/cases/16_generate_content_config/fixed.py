from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent
from google.genai import types

def create_agent(model_name: str) -> BaseAgent:
    """
    Creates an LlmAgent configured with `generate_content_config`.

    This function represents the correct implementation for benchmark testing.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of LlmAgent with a configured content generation setup.
    """
    agent = LlmAgent(
        name="config_agent",
        model=model_name,
        instruction="You are a helpful assistant. Always respond with 'Hello world!'",
        generate_content_config=types.GenerationConfig(temperature=0.0),
    )
    return agent
