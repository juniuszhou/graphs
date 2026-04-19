from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass
from pydantic import BaseModel, Field


def different_state_classes():
    # three different way to define a state class
    class AgentState(TypedDict):
        message: str
        context: str
        history: Optional[str]

    @dataclass
    class AgentState:
        message: Annotated[str, Field(default="")]
        context: str = ""
        history: Optional[str]

    class AgentState(BaseModel):
        message: str
        context: str
        history: Optional[str]

    # define a node
    def node_one(state: AgentState) -> AgentState:
        """Greeting node"""
        state["message"] = "I am node one"
        state["context"] = "It is start of the graph"
        return state

    # () can be used to define a bunch of operations with the returned value of the first function.
    graph = (
        StateGraph(AgentState)
        .add_node(node_one)
        .add_edge(START, "node_one")
        .add_edge("node_one", END)
        .compile(name="basic_graph")
    )

    # the result the final state of the graph.
    result = graph.invoke({})
    print("result as: \n", result)


# different state for different channels
def different_state_channel():
    class AgentState1(TypedDict):
        message: str

    class AgentState2(TypedDict):
        message: str

    # define a node
    def node_one(state: AgentState1) -> AgentState2:
        return {"message": state["message"]}

    def node_two(state: AgentState2) -> AgentState1:
        return {"message": "back to state 1"}

    # () can be used to define a bunch of operations with the returned value of the first function.
    graph = (
        StateGraph(AgentState1)
        .add_node(node_one)
        .add_node(node_two)
        .add_edge(START, "node_one")
        .add_edge("node_one", "node_two")
        .add_edge("node_two", END)
        .compile(name="basic_graph")
    )

    # the result the final state of the graph.
    result = graph.invoke({"message": "I am node one"})
    print("result as: \n", result)


different_state_channel()
