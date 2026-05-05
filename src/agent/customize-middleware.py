import sys
from pathlib import Path
from typing import Any
from langchain.agents import create_agent
from langchain.agents.middleware import (
    before_model, 
    after_model, 
    wrap_model_call,
    AgentState,
    Runtime,
    AgentMiddleware,hook_config
)
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm

class MyMiddleware(AgentMiddleware):
    def __init__(self, max_tokens=10000):
        super().__init__()
        self.max_tokens = max_tokens

    @hook_config(can_jump_to=["end"])
    def before_model(self, state: AgentState, runtime: Runtime):
        print("before model")

    def after_model(self, state: AgentState, runtime: Runtime):
        print("after model")

@before_model()
def print_before_model(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Send an email to a recipient."""
    print("before model")


@after_model()
def print_after_model(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Send an email to a recipient."""
    print("after model")

agent = create_agent(
    model=gemma_llm,
    tools=[],
    middleware=[
        print_before_model,
        print_after_model,
        MyMiddleware(),
    ],
    system_prompt=(
        "You are a helpful assistant. Use the send_email tool when the user asks "
        "you to send an email."
    ),
)

def run_edit_example() -> None:
    """You are a helpful assistant."""
    config = {"configurable": {"thread_id": "hitl-email-edit-demo"}}

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "say Hello to the world.",
                }
            ]
        },
        config=config,
    )

    
    print(result)


if __name__ == "__main__":
    run_edit_example()
