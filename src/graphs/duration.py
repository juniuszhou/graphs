import uuid
from typing import Optional, TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.graph import StateGraph, START, END


# define a state
class AgentState(TypedDict):
    message: str
    context: str
    history: Optional[str]


# define a node
def node_one(state: AgentState) -> AgentState:
    """Greeting node"""
    state["message"] = "I am node one"
    state["context"] = "It is start of the graph"
    return state


def node_two(state: AgentState) -> AgentState:
    """Greeting node"""
    print("==== before me, the message is: ", state["message"])
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
    durability="sync",
)
print("result as: \n", result)
