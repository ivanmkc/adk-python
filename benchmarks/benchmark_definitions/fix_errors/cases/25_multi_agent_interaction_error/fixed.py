from __future__ import annotations
from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a SequentialAgent that correctly manages inter-agent communication.

  The `writer_agent` sets a value in session state, which the `reader_agent` then correctly retrieves.
  This function represents the correct implementation (ground truth) for benchmark testing.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of SequentialAgent with correct multi-agent interaction.
  """
  MODEL_NAME = model_name  # Local variable for the snippet

  writer_agent = LlmAgent(
      name="writer_agent",
      model=MODEL_NAME,
      instruction="Respond with only the text 'secret_message'.",
      output_key="correct_key",
  )

  reader_agent = LlmAgent(
      name="reader_agent",
      model=MODEL_NAME,
      instruction=(
          "Your only task is to output the content of '{correct_key}'. Do not"
          " add any other text."
      ),
  )

  root_agent = SequentialAgent(
      name="multi_agent_coordinator",
      sub_agents=[writer_agent, reader_agent],
  )
  return root_agent
