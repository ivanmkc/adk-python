from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.tools import AgentTool
from pydantic import BaseModel, Field


class UserInfo(BaseModel):
  name: str = Field(description="The user's name.")
  age: int = Field(description="The user's age.")


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a buggy LlmAgent with an incorrect or missing input schema.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of BaseAgent, expected to fail in input schema validation.
  """
  raise NotImplementedError("Agent not implemented for unfixed version.")
