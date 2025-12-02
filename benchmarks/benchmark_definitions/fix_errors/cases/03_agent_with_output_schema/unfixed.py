from __future__ import annotations
from google.adk.agents import LlmAgent, BaseAgent
from pydantic import BaseModel, Field


class BasicOutputSchema(BaseModel):
  field_one: str = Field(description="The first field.")
  field_two: int = Field(description="The second field.")


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates an LlmAgent that enforces JSON output using `output_schema`.

  Instructions:
      Create an LlmAgent named "output_schema_agent" that uses `BasicOutputSchema`
      to enforce structured JSON output.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of LlmAgent with a configured output schema.
  """
  raise NotImplementedError("Agent implementation incomplete.")
