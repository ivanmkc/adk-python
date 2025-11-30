from __future__ import annotations
from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent

def create_agent(model_name: str) -> BaseAgent:
    """
    Creates a buggy SequentialAgent with incorrect sub-agent configuration.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of BaseAgent, expected to fail in sequential execution.
    """
    raise NotImplementedError("Agent not implemented for unfixed version.")
