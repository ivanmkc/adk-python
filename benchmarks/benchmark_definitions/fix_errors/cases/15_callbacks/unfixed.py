from __future__ import annotations

from google.adk.agents import BaseAgent
from google.adk.agents import LlmAgent

callback_was_called = False


def my_callback(**kwargs) -> None:
  """A simple callback that sets a flag."""
  global callback_was_called
  callback_was_called = True
  print("Callback was executed.")


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates an LlmAgent with an `after_model_callback` configured.

  Instructions:
      Create an LlmAgent named "callback_agent" that registers the `my_callback` function
      as its `after_model_callback`.

      Requirements:
      - The agent should use the `my_callback` function as its `after_model_callback`.
      - The agent should respond to a greeting with a response containing 'Hello'.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent with a configured after-model callback.
  """
  raise NotImplementedError("Agent implementation incomplete.")
