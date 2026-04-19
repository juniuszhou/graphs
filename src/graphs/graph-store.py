from langgraph.graph import StateGraph, START, END
from langgraph.config import get_store
from langgraph.store.memory import InMemoryStore
from typing import TypedDict


# define a state
class AgentState(TypedDict):
    message: str
    context: str


# define a node
def node_one(state: AgentState) -> AgentState:
    """Greeting node — store is only available via get_store() inside a running graph."""
    store = get_store()
    item = store.get(("topic",), "main")
    topic = item.value["text"] if item else None
    print("we get topic in node one: ", topic)
    return state


def node_two(state: AgentState) -> AgentState:
    """Greeting node"""
    print("==== before me, the message is: ", state["message"])
    state["history"] = state["message"]
    state["message"] = "I am node two"

    return state


store = InMemoryStore()

# () can be used to define a bunch of operations with the returned value of the first function.
graph = (
    StateGraph(AgentState)
    .add_node(node_one)
    .add_node(node_two)
    .add_edge(START, "node_one")
    .add_edge("node_one", "node_two")
    .add_edge("node_two", END)
    .compile(name="basic_graph", store=store)
)

# After compile(store=...), use the same object or graph.store (identical reference).
graph.store.put(("topic",), "main", {"text": "chickens"})

# the result the final state of the graph.
result = graph.invoke({"message": "", "context": ""})
print("result as: \n", result)
