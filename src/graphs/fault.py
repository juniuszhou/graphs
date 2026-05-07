"""Example of a basic graph with retry_policy."""

import logging
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.types import RetryPolicy, default_retry_on


class MyCustomError(Exception):
    """Custom error."""


def custom_retry_on(exc: BaseException) -> bool:
    """Define a custom retry on function."""
    if isinstance(exc, MyCustomError):
        return False
    return default_retry_on(exc)


# define a state
class AgentState(TypedDict):
    """State of the agent."""

    message: str
    context: str
    history: str | None


# define a node
def node_one(state: AgentState, runtime: Runtime) -> AgentState:
    """Greeting node."""
    if runtime.execution_info.node_attempt > 1:
        raise MyCustomError("MyCustomError")
    state["message"] = "I am node one"
    state["context"] = "It is start of the graph"
    return state


def node_two(state: AgentState) -> AgentState:
    """Greeting node."""
    logging.warning("==== before me, the message is: %s", state["message"])
    state["history"] = state["message"]
    state["message"] = "I am node two"

    return state


# () can be used to define a bunch of operations with the returned value of the first function.
graph = (
    StateGraph(AgentState)
    # retry_policy is a list of RetryPolicy, if the node fails, it will retry the node.
    .add_node(node_one, retry_policy=RetryPolicy(max_retries=3, retry_on=Exception))
    .add_node(
        node_two,
        retry_policy=RetryPolicy(max_retries=3, retry_on=custom_retry_on),
        timeout=TimeoutPolicy(timeout=10),
    )
    .add_edge(START, "node_one")
    .add_edge("node_one", "node_two")
    .add_edge("node_two", END)
    .compile(name="basic_graph")
)

# the result the final state of the graph.
result = graph.invoke({"message": "Hello World", "context": "", "history": None})
logging.warning("result as: \n %s", result)
