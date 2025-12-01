from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent
from pydantic import BaseModel, Field


class BasicOutputSchema(BaseModel):
  field_one: str = Field(description="The first field.")
  field_two: int = Field(description="The second field.")


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a buggy LlmAgent with an incorrect or missing output schema.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of BaseAgent, expected to fail in output schema validation.
  """
  raise NotImplementedError("Agent not implemented for unfixed version.")
