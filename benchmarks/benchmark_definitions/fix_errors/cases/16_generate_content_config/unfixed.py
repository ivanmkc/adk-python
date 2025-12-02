from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent
from google.genai import types


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates an LlmAgent configured with `generate_content_config`.

  Instructions:
      Create an LlmAgent named "config_agent" that responds with "Hello world!".
      Configure the agent to use a temperature of 0.0 via `generate_content_config`.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent with a configured content generation setup.
  """
  raise NotImplementedError("Agent implementation incomplete.")
