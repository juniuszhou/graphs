from typing import TypedDict, Dict, Optional
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
    state["message"] = "I am node two"
    state["context"] = "It is start of the graph"
    return state


def node_three(state: AgentState) -> AgentState:
    """Greeting node"""
    state["message"] = "I am node three"
    state["context"] = "It is start of the graph"
    return state


def router_node(state: AgentState) -> str:
    """Greeting node"""
    if state["message"] == "I am node one":
        return "node_two"
    else:
        return END


# () can be used to define a bunch of operations with the returned value of the first function.
graph = (
    StateGraph(AgentState)
    .add_node(node_one)
    .add_node(node_two)
    .add_node("router_node", router_node)
    .add_edge(START, "node_one")
    # after node_one, the graph will be routed to node_two or END.
    # we should not define the edge from node_one to router_node.
    .add_conditional_edges(
        "node_one",
        router_node,
        {
            "node_two": "node_two",
            END: END,
        },
    )
    .compile(name="basic_graph")
)

# the result the final state of the graph.
result = graph.invoke({})
print("result as: \n", result)
