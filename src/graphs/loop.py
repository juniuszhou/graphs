# demo how to define a loop in a graph
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List


class AgentState(TypedDict):
    numbers: List[int]
    result: int


def add_numbers(state: AgentState) -> AgentState:
    """Add numbers"""
    print("add_numbers", state["numbers"])
    first_number = state["numbers"][0]
    numbers = state["numbers"][1:]
    state["result"] = state["result"] + first_number
    state["numbers"] = numbers
    return state


def loop_node(state: AgentState) -> AgentState:
    """Loop node"""
    print("loop_node", state["numbers"])

    if len(state["numbers"]) > 0:
        return "loop"
    else:
        return "exit"


graph = StateGraph(AgentState)
graph.add_node("add_numbers", add_numbers)
graph.add_node("loop", loop_node)

graph.add_edge(START, "add_numbers")
# graph.add_edge("add_numbers", "loop")
graph.add_conditional_edges(
    "add_numbers", loop_node, {"loop": "add_numbers", "exit": END}
)

app = graph.compile()

result = app.invoke({"numbers": [1, 2, 3, 4, 5], "result": 0})
print(result["result"])
