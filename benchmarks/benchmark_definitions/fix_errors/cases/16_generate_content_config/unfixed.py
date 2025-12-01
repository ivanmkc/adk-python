from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent
from google.genai import types


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a buggy LlmAgent with an incorrect or missing generate_content_config.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of BaseAgent, expected to fail in content generation.
  """
  raise NotImplementedError("Agent not implemented for unfixed version.")
