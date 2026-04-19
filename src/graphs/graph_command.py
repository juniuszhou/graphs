from typing import TypedDict, Dict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import Literal


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


# command decide the next node to go and state. don't need add the edge here.
def command_agent(state: AgentState) -> Command[Literal["node_two", END]]:
    if state["message"] == "I am node one":
        print("==== command_agent: goto node_two")
        return Command(goto="node_two", update={"messages": ["response"]})
    return Command(goto=END, update={"messages": ["response"]})


def node_two(state: AgentState) -> AgentState:
    """Greeting node"""
    print("==== before me, the message is: ", state["message"])
    state["history"] = state["message"]
    state["message"] = "I am node two"

    return state


# () can be used to define a bunch of operations with the returned value of the first function.
graph = (
    StateGraph(AgentState)
    .add_node(node_one)
    .add_node(node_two)
    .add_node("command_agent", command_agent)
    .add_edge(START, "node_one")
    .add_edge("node_one", "command_agent")
    # no edge from command_agent to node_two or END.
    # from here, we can see the END is not must have.
    # after the message go to node_two, there is no following node. the call will be terminated.
    .compile(name="basic_graph")
)

# the result the final state of the graph.
result = graph.invoke({})
print("result as: \n", result)
