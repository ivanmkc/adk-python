from __future__ import annotations
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event


class CustomConditionalAgent(BaseAgent):
  """A custom agent that runs one of two sub-agents based on session state."""

  agent_a: LlmAgent
  agent_b: LlmAgent

  async def _run_async_impl(
      self, ctx: InvocationContext
  ) -> AsyncGenerator[Event, None]:
    should_run_a = ctx.session.state.get("run_agent_a", False)

    if should_run_a:
      async for event in self.agent_a.run_async(ctx):
        yield event
    else:
      async for event in self.agent_b.run_async(ctx):
        yield event


def create_agent(model_name: str) -> BaseAgent:
  """
  Creates a custom agent with conditional logic based on session state.

  This function represents the correct implementation for benchmark testing.

  Args:
      model_name: The name of the LLM model to use.

  Returns:
      An instance of CustomConditionalAgent.
  """
  agent_a = LlmAgent(
      name="agent_a",
      model=model_name,
      instruction="Respond with only the text: Agent A was chosen.",
  )
  agent_b = LlmAgent(
      name="agent_b",
      model=model_name,
      instruction="Respond with only the text: Agent B was chosen.",
  )

  root_agent = CustomConditionalAgent(
      name="custom_conditional_agent",
      agent_a=agent_a,
      agent_b=agent_b,
      sub_agents=[agent_a, agent_b],
  )
  return root_agent
