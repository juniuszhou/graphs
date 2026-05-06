import sys
from pathlib import Path
from pprint import pprint
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm

from langchain.agents.middleware import dynamic_prompt, wrap_model_call, ModelRequest, ModelResponse

# get the context from the state, runtime, store, etc.
# then return a dynamic prompt for the agent.
# it is wrapped as a middleware.
# in this way, we can provide a dynamic prompt for the agent.
@dynamic_prompt
def state_aware_prompt(request: ModelRequest) -> str:
    # request.messages is a shortcut for request.state["messages"]
    message_count = len(request.messages)

    user_role = request.runtime.context.user_role
    env = request.runtime.context.deployment_env

    store = request.runtime.store

    base = "You are a helpful assistant."

    if message_count > 10:
        base += "\nThis is a long conversation - be extra concise."

    return base

@wrap_model_call
def state_aware_model_call(request: ModelRequest) -> ModelResponse:
    return request
# before the agent starts, after it completes, or around model and tool calls.

agent = create_agent(
    model=gemma_llm,
    tools=[],
    middleware=[state_aware_prompt, state_aware_model_call],
    system_prompt=(
        "You are a helpful assistant. Use the send_email tool when the user asks "
        "you to send an email."
    ),
)

@wrap_model_call
def state_based_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Select model based on State conversation length."""
    # request.messages is a shortcut for request.state["messages"]
    message_count = len(request.messages)

    if message_count > 20:
        # Long conversation - use model with larger context window
        model = large_model
    elif message_count > 10:
        # Medium conversation
        model = standard_model
    else:
        # Short conversation - use efficient model
        model = efficient_model

    request = request.override(model=model)

    return handler(request)
    
result = agent.invoke({
    "messages": [{"role": "user", "content": "My email is john.doe@example.com and card is 5105-1051-0510-5100"}]
})

pprint(result)