"""Example of a basic graph."""

import logging
from typing import TypedDict

from langgraph.func import task
from langgraph.graph import END, START, StateGraph


@task()
def task_one(state: AgentState) -> AgentState:
    """Task one.

    task can be called in other task or node.
    @task 告诉 LangGraph：这个函数不是普通函数调用，而是 workflow 里的一个可追踪、可调度、可组合的执行单元。
    它不是一个定义好的graph里面的静态节点，像是一个动态节点。
    它是Functional API 的一部分，可以被其他任务或节点调用。
    """
    state["task_impact"] = "I am task one"
    logging.warning("task one: %s", state["task_impact"])
    return state


# define a state
class AgentState(TypedDict):
    """State of the agent."""

    message: str
    context: str
    history: str | None
    task_impact: str | None


# define a node
def node_one(state: AgentState) -> AgentState:
    """Greeting node."""
    # @task calls return a Future; use .result() so the task's return value
    # (including task_impact) is applied. Discarding the future drops that update.
    state = task_one(state).result()
    state["message"] = "I am node one"
    state["context"] = "It is start of the graph"
    return state


def node_two(state: AgentState) -> AgentState:
    """Greeting node."""
    logging.warning("==== before me, the message is: %s", state["message"])
    state["history"] = state["message"]
    state["message"] = "I am node two"

    return state


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
# result = graph.invoke({"message": "Hello World", "context": "", "history": None})
# logging.warning("result as: \n %s", result)
