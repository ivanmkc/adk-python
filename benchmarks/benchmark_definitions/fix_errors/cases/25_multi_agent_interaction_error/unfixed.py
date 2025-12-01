from __future__ import annotations
from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a SequentialAgent with an interaction error between sub-agents.

  The `writer_agent` fails to correctly set a value in session state,
  preventing the `reader_agent` from accessing it.
  This simulates a broken multi-agent communication flow.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of SequentialAgent with a multi-agent interaction error.
  """
  # Error: reader_agent references {correct_key} but writer_agent outputs to output_key="wrong_key" (implicitly or explicitly different)
  # Here we explicitly set output_key to something else or don't set it (default output not captured in state unless key is set).
  writer_agent = LlmAgent(
      name="writer_agent",
      model=model_name,
      instruction="Respond with only the text 'secret_message'.",
      # Missing output_key="correct_key"
  )

  reader_agent = LlmAgent(
      name="reader_agent",
      model=model_name,
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
