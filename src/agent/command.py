from operator import add
from typing import Annotated, Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Send, interrupt


class DemoState(TypedDict):
    """Shared graph state for the Command examples."""

    topic: str
    route: str
    human_answer: str
    log: Annotated[list[str], add]


def show(title: str, value) -> None:
    """Print a small section header and result."""
    print(f"\n{'=' * 20} {title} {'=' * 20}")
    print(value)


def command_update_node(state: DemoState) -> Command[Literal["after_update"]]:
    """Command(update=...) changes state and Command(goto=...) chooses the next node."""
    return Command(
        update={"topic": "updated by Command.update", "log": ["update_node changed state"]},
        goto="after_update",
    )


def after_update_node(state: DemoState) -> dict:
    """Read the state written by the previous Command."""
    return {"log": [f"after_update saw topic={state['topic']!r}"]}


def run_update_and_goto_demo() -> None:
    """Show Command.update and Command.goto in one tiny graph."""
    graph = (
        StateGraph(DemoState)
        .add_node("update_node", command_update_node)
        .add_node("after_update", after_update_node)
        .add_edge(START, "update_node")
        # No edge from update_node to after_update is needed because Command.goto does it.
        .add_edge("after_update", END)
        .compile()
    )

    result = graph.invoke({"topic": "original", "route": "", "human_answer": "", "log": []})
    show("Command(update=...) + Command(goto=...)", result)


def router_node(state: DemoState) -> Command[Literal["left_node", "right_node"]]:
    """Route dynamically based on state."""
    if state["route"] == "left":
        return Command(update={"log": ["router chose left"]}, goto="left_node")

    return Command(update={"log": ["router chose right"]}, goto="right_node")


def left_node(state: DemoState) -> dict:
    return {"log": ["left_node ran"]}


def right_node(state: DemoState) -> dict:
    return {"log": ["right_node ran"]}


def run_dynamic_goto_demo() -> None:
    """Show Command.goto as a runtime router."""
    graph = (
        StateGraph(DemoState)
        .add_node("router", router_node)
        .add_node("left_node", left_node)
        .add_node("right_node", right_node)
        .add_edge(START, "router")
        .add_edge("left_node", END)
        .add_edge("right_node", END)
        .compile()
    )

    result = graph.invoke({"topic": "", "route": "left", "human_answer": "", "log": []})
    show("Command(goto='left_node')", result)


def fanout_node(state: DemoState) -> Command:
    """Use Command.goto with Send objects to run the same node with custom inputs."""
    return Command(
        goto=[
            Send("worker_node", {"topic": "alpha", "route": "", "human_answer": "", "log": []}),
            Send("worker_node", {"topic": "beta", "route": "", "human_answer": "", "log": []}),
        ]
    )


def worker_node(state: DemoState) -> dict:
    return {"log": [f"worker handled {state['topic']}"]}


def run_send_demo() -> None:
    """Show Command.goto with Send for fan-out work."""
    graph = (
        StateGraph(DemoState)
        .add_node("fanout", fanout_node)
        .add_node("worker_node", worker_node)
        .add_edge(START, "fanout")
        .add_edge("worker_node", END)
        .compile()
    )

    result = graph.invoke({"topic": "", "route": "", "human_answer": "", "log": []})
    show("Command(goto=[Send(...), Send(...)])", result)


def ask_human_node(state: DemoState) -> dict:
    """Pause the graph and wait for Command(resume=...)."""
    answer = interrupt("What should the graph remember?")
    return {"human_answer": answer, "log": [f"human answered {answer!r}"]}


def run_resume_demo() -> None:
    """Show Command.resume after an interrupt."""
    graph = (
        StateGraph(DemoState)
        .add_node("ask_human", ask_human_node)
        .add_edge(START, "ask_human")
        .add_edge("ask_human", END)
        .compile(checkpointer=InMemorySaver())
    )
    config = {"configurable": {"thread_id": "command-resume-demo"}}

    interrupted = graph.invoke(
        {"topic": "", "route": "", "human_answer": "", "log": []},
        config=config,
        version="v2",
    )
    show("interrupt before Command(resume=...)", interrupted.interrupts)

    result = graph.invoke(Command(resume="remember this value"), config=config, version="v2")
    show("Command(resume='remember this value')", result.value)


def child_jump_to_parent(state: DemoState) -> Command:
    """Inside a subgraph, jump back to a node in the parent graph."""
    return Command(
        graph=Command.PARENT,
        update={"log": ["child graph jumped to parent_finish"]},
        goto="parent_finish",
    )


def parent_finish_node(state: DemoState) -> dict:
    return {"log": ["parent_finish ran"]}


def run_parent_graph_demo() -> None:
    """Show Command(graph=Command.PARENT) from a subgraph."""
    child_graph = (
        StateGraph(DemoState)
        .add_node("child_jump", child_jump_to_parent)
        .add_edge(START, "child_jump")
        .compile()
    )
    parent_graph = (
        StateGraph(DemoState)
        .add_node("child_graph", child_graph)
        .add_node("parent_finish", parent_finish_node)
        .add_edge(START, "child_graph")
        .add_edge("parent_finish", END)
        .compile()
    )

    result = parent_graph.invoke({"topic": "", "route": "", "human_answer": "", "log": []})
    show("Command(graph=Command.PARENT, goto='parent_finish')", result)

# Command here just use the Command in the langgraph directly.
if __name__ == "__main__":
    run_update_and_goto_demo()
    run_dynamic_goto_demo()
    run_send_demo()
    run_resume_demo()
    run_parent_graph_demo()