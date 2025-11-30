from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent

callback_was_called = False

def my_callback(**kwargs) -> None:
    """A simple callback that sets a flag."""
    global callback_was_called
    callback_was_called = True
    print("Callback was executed.")

def create_agent(model_name: str) -> BaseAgent:
    """
    Creates a buggy LlmAgent with an incorrect or missing after_model_callback.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of BaseAgent, expected to fail in callback execution.
    """
    raise NotImplementedError("Agent not implemented for unfixed version.")
