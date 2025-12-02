from __future__ import annotations
from google.adk.agents import LlmAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates an LlmAgent with the necessary import statement.

  Instructions:
      Create an LlmAgent named "import_agent".
      Ensure all necessary modules (like LlmAgent) are imported.

      Requirements:
      - The agent should be a valid LlmAgent instance.
      - The agent should respond to the greeting 'Hello' with a response containing 'Hello'.
      - The final solution must be assigned to a variable named `root_agent`.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent.
  """
  raise NameError("name 'LlmAgent' is not defined")
