from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates an LlmAgent that utilizes artifact data in its instructions.

  Instructions:
      Create an LlmAgent named "artifact_agent" that references the artifact
      `{artifact.my_data}` in its instructions.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent capable of using artifact data.
  """
  raise NotImplementedError("Agent implementation incomplete.")
