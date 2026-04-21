# how to use the conditional edges in graph
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, START, END


# define a state
class AgentState(TypedDict):
    op1: int
    op2: int
    operator: str
    result: int


# define a node
def adder(state: AgentState) -> AgentState:
    """Greeting node"""
    result = state["op1"] + state["op2"]
    state["result"] = result
    return state


def subtractor(state: AgentState) -> AgentState:
    """Subtractor node"""
    result = state["op1"] - state["op2"]
    state["result"] = result
    return state


def router(state: AgentState) -> AgentState:
    """Router node"""
    if state["operator"] == "+":
        return "adder_op"
    elif state["operator"] == "-":
        return "subtractor_op"


graph = StateGraph(AgentState)

adder_node = graph.add_node("adder", adder)
subtractor_node = graph.add_node("subtractor", subtractor)
router_node = graph.add_node("router", lambda state: state)

graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router", router, {"adder_op": "adder", "subtractor_op": "subtractor"}
)
graph.add_edge("adder", END)
graph.add_edge("subtractor", END)

app = graph.compile()

result = app.invoke({"op1": 10, "op2": 2, "operator": "-"})
print(result["result"])
