from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.tools import AgentTool
from pydantic import BaseModel, Field


class UserInfo(BaseModel):
  name: str = Field(description="The user's name.")
  age: int = Field(description="The user's age.")


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates an LlmAgent that uses `input_schema` for structured input.

  Instructions:
      Create a "worker" agent that accepts user info (name: str, age: int) via `input_schema`.
      Then, create a root "agent" that uses the worker as a tool to process user info.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent with a configured input schema.
  """
  raise NotImplementedError("Agent implementation incomplete.")
