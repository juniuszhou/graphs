from typing import TypedDict, Dict, Optional
from langgraph.graph import StateGraph, START, END
from asyncio import run


# define a state
class AgentState(TypedDict):
    message: str
    context: str
    history: Optional[str]


# define a node
async def node_one(state: AgentState) -> AgentState:
    """Greeting node"""
    state["message"] = "I am node one"
    state["context"] = "It is start of the graph"
    return state


async def node_two(state: AgentState) -> AgentState:
    """Greeting node"""
    print("==== before me, the message is: ", state["message"])
    state["history"] = state["message"]
    state["message"] = "I am node two"

    return state


async def main():

    # () can be used to define a bunch of operations with the returned value of the first function.
    graph = (
        StateGraph(AgentState)
        .add_node(node_one)
        .add_node(node_two)
        .add_edge(START, "node_one")
        .add_edge("node_one", "node_two")
        .add_edge("node_two", END)
        .compile(name="basic_graph")
    )

    # the result the final state of the graph.
    result = await graph.ainvoke({"topic": "ice cream"})
    print("result as: \n", result)


if __name__ == "__main__":
    run(main())
