"""Example of using duration to store the state of the graph.

Duration is a feature that allows you to store the state of the graph.
It is a feature that allows you to store the state of the graph.
It is a feature that allows you to store the state of the graph.
"""

import logging
import uuid
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


# define a state
class AgentState(TypedDict):
    """State of the agent."""

    message: str
    context: str
    history: str | None


# define a node
def node_one(state: AgentState) -> AgentState:
    """Add message to the state."""
    state["message"] = "I am node one"
    state["context"] = "It is start of the graph"
    return state


def node_two(state: AgentState) -> AgentState:
    """Append message to the state."""
    logging.info("==== before me, the message is: ", state["message"])
    state["history"] = state["message"]
    state["message"] = "I am node two"

    return state


# Durability mode is set on invoke/stream, not on compile. Requires a checkpointer + thread_id.
checkpointer = InMemorySaver()
run_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

# () can be used to define a bunch of operations with the returned value of the first function.
graph = (
    StateGraph(AgentState)
    .add_node(node_one)
    .add_node(node_two)
    .add_edge(START, "node_one")
    .add_edge("node_one", "node_two")
    .add_edge("node_two", END)
    .compile(name="basic_graph", checkpointer=checkpointer)
)

# the result the final state of the graph.
result = graph.invoke(
    {"message": "", "context": ""},
    run_config,
    # durability="sync"  or "async" or "exit"
    # sync: persist after each superstep, guarantee persist is completed
    # async: persist async, no guarantee persist is completed
    # exit: persist only when program exit. no persist if crash.
    durability="sync",
)
logging.info("result as: \n", result)
