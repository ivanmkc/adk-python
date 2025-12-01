from __future__ import annotations
from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a SequentialAgent that demonstrates inter-agent state management.

  A 'writer' agent stores a value in session state, which a 'reader' agent then retrieves.
  This function represents the correct implementation for benchmark testing.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of SequentialAgent with state-managing sub-agents.
  """
  writer_agent = LlmAgent(
      name="writer_agent",
      model=model_name,
      instruction=(
          "Your sole task is to output the string 'xyz'. Do not add any other"
          " text."
      ),
      output_key="secret_word",
  )

  reader_agent = LlmAgent(
      name="reader_agent",
      model=model_name,
      instruction=(
          "The secret word is {secret_word}. Your task is to simply repeat that"
          " secret word."
      ),
  )

  root_agent = SequentialAgent(
      name="state_management_coordinator",
      sub_agents=[writer_agent, reader_agent],
  )
  return root_agent
