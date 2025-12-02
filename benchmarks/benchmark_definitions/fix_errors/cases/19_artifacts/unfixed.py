from __future__ import annotations

from google.adk.agents import BaseAgent
from google.adk.agents import LlmAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates an LlmAgent that utilizes artifact data in its instructions.

  Instructions:
      Create an LlmAgent named "artifact_agent" that references the artifact
      `{artifact.my_data}` in its instructions.

      Requirements:
      - The agent's instruction should reference an artifact named 'my_data'.
      - The agent should directly state the content of the 'my_data' artifact in its response.
      - The final solution must be assigned to a variable named `agent`.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent capable of using artifact data.
  """
  raise NotImplementedError("Agent implementation incomplete.")
