import operator
from typing import Annotated, NotRequired, Optional, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


# Parallel branches (e.g. from Send) may update the same key in one step — use a reducer.
# Keys only present on `Send(..., arg)` for a branch are optional on the full state.
class AgentState(TypedDict):
    message: Annotated[list[str], operator.add]
    context: str
    history: Optional[str]
    handoff: NotRequired[str]


# define a node
def node_one(state: AgentState) -> AgentState:
    """Greeting node"""
    state["message"] = ["I am node one"]
    state["context"] = "It is start of the graph"
    return state


def node_two(state: AgentState):
    # Second arg to Send(...) is the input dict passed to that node (see LangGraph `Send` docs).
    # `node_two` sees the full state after `node_one`; put anything downstream should read here.
    base = dict(state)
    return [
        Send(
            "node_three",
            {**base, "handoff": "node_two → node_three"},
        ),
        Send(
            "node_four",
            {**base, "handoff": "node_two → node_four"},
        ),
    ]


def node_three(state: AgentState) -> dict:
    # `handoff` (and the rest) arrived via Send from `node_two`.
    return {"message": [f"I am node three ({state.get('handoff', '')})"]}


def node_four(state: AgentState) -> dict:
    print("==== I am node four, the state is: ", state)
    # from here, we can see the message from node_two should be in the state.
    # the only way we can get it is from the state.get('handoff', '')
    return {**state, "message": [f"I am node four ({state.get('handoff', '')})"]}


graph = (
    StateGraph(AgentState)
    .add_node(node_one)
    .add_node(node_two)
    .add_node(node_three)
    .add_node(node_four)
    .add_edge(START, "node_one")
    .add_conditional_edges(
        "node_one",
        node_two,
        {
            "node_three": "node_three",
            "node_four": "node_four",
        },
    )
    .add_edge("node_three", END)
    .add_edge("node_four", END)
    .compile(name="basic_graph")
)

# the final handoff should be the node_two → node_four. according to the order of the nodes.
# so the message should be I am node four (node_two → node_four).
result = graph.invoke({})
print("result as: \n", result)
print("the message should be: \n", result["message"])
