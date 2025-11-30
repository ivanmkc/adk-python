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

    This function represents the correct implementation for benchmark testing.

    Args:
        model_name: The name of the LLM model to use.

    Returns:
        An instance of LlmAgent with a configured input schema.
    """
    worker_agent = LlmAgent(
        name="worker",
        model=model_name,
        instruction="Acknowledge the user's name and age.",
        input_schema=UserInfo,
    )
    agent = LlmAgent(
        name="agent",
        model=model_name,
        tools=[AgentTool(agent=worker_agent)],
        instruction="Use the worker agent to process the user's info.",
    )
    return agent
