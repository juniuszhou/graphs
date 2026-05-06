# different runs in one graph
# - LLM run
# - Tool run
# - Retriever run, get documents from db or other sources
# - parser
# - chain
# - prompt generate the prompt for LLM

from typing import TypedDict, Dict, Optional
from langgraph.graph import StateGraph, START, END
from langsmith import traceable
from typing import List
# define a state
class AgentState(TypedDict):
    message: str
    context: str
    history: Optional[str]

# reduce the trace to a single string via concatenate all the trace strings
def reduce_trace(trace: List):
    joined_trace = "\n".join(trace)
    return joined_trace
# define the trace with some attributes
@traceable(
    run_type="llm",
    metadata={"run_name": "node_one"},
    tags=["llm", "tool", "retriever", "parser", "chain", "prompt"],
    reduce_fn=reduce_trace,
)
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