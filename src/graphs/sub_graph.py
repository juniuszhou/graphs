from typing_extensions import TypedDict
from langgraph.graph.state import StateGraph, START


# create a subgraph, then call it via invoke functon
def call_subgraph():
    class SubgraphState(TypedDict):
        bar: str

    def subgraph_node_1(state: SubgraphState):
        return {"bar": "subgraph node! " + state["bar"]}

    subgraph_builder = StateGraph(SubgraphState)
    subgraph_builder.add_node(subgraph_node_1)
    subgraph_builder.add_edge(START, "subgraph_node_1")
    # checkpointer could be None, True and False.
    # None per-invocation, each call start from scratch and inherit the checkpointer from the parent graph.
    # True per-thread state accumulates across calls in the same thread.
    # False per-graph no checkpointing.
    subgraph = subgraph_builder.compile()

    class State(TypedDict):
        foo: str

    def call_subgraph(state: State):
        # Transform the state to the subgraph state
        subgraph_output = subgraph.invoke({"bar": state["foo"]})
        # Transform response back to the parent state
        return {"foo": subgraph_output["bar"]}

    builder = StateGraph(State)
    builder.add_node("node_1", call_subgraph)
    builder.add_edge(START, "node_1")
    graph = builder.compile()

    result = graph.invoke({"foo": "world"})
    print(result)


# add a subgraph to a parent graph
def add_subgraph():
    class State(TypedDict):
        foo: str

    def subgraph_node_1(state: State):
        return {"foo": "subgraph node! " + state["foo"]}

    subgraph_builder = StateGraph(State)
    subgraph_builder.add_node(subgraph_node_1)
    subgraph_builder.add_edge(START, "subgraph_node_1")
    subgraph = subgraph_builder.compile()

    builder = StateGraph(State)
    builder.add_node("node_1", subgraph)
    builder.add_edge(START, "node_1")
    graph = builder.compile()

    result = graph.invoke({"foo": "world"})
    print(result)


call_subgraph()
add_subgraph()
