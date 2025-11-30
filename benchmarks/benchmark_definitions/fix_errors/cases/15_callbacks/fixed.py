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
    Creates an LlmAgent with an `after_model_callback` configured.

    This function represents the correct implementation for benchmark testing.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of LlmAgent with a configured after-model callback.
    """
    root_agent = LlmAgent(
        name="callback_agent",
        model=model_name,
        instruction="You are a helpful assistant.",
        after_model_callback=my_callback,
    )
    return root_agent
