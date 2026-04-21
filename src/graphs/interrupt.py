from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, END, START
from langgraph.types import Interrupt, interrupt, Send, Command
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    ToolMessage,
)
from operator import add as add_messages
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool

load_dotenv()


def print_interrupt_in_result(result: list):
    if "__interrupt__" in result:
        interrupt_list = result["__interrupt__"]
        if interrupt_list:
            interrupt_message = interrupt_list[0]  # Get the first Interrupt object
            print(f"\nInterrupt value: {interrupt_message.value}")
            print(f"Interrupt id: {interrupt_message.id}")
    else:
        print("No interrupt found in the result")


llm = ChatOpenAI(
    model="llama3.2:3b",
    temperature=0,
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


class AgentState(TypedDict):
    messages: str


def start_node(state: AgentState) -> AgentState:
    return {"messages": state["messages"] + "Hello, how are you?"}


def end_node(state: AgentState) -> AgentState:
    return {"messages": state["messages"] + "I am fine, thank you!"}


def interrupt_node(state: AgentState) -> AgentState:
    # interrupt here and wait for the human to input the problem.
    problem = interrupt({"error": "what is your problem?"})
    print("problem description from human: ", problem)
    return {"messages": problem}


# to demo how to interrupt like static way. to ask the graph to interrupt at a specific node.
# this is not the recommended way to debug the graph.
def interrupt_as_debug():
    graph = (
        StateGraph(AgentState)
        .add_node("start_node", start_node)
        .add_node("interrupt_node", interrupt_node)
        .add_node("end_node", end_node)
        .add_edge(START, "start_node")
        .add_edge("start_node", "interrupt_node")
        .add_edge("interrupt_node", "end_node")
        .add_edge("end_node", END)
        .compile(
            # interrupt_before=["start_node"],
            interrupt_after=["end_node"],
        )
    )
    result = graph.invoke({"messages": "Input message from the user."})
    print_interrupt_in_result(result)


def simple_interrupt_graph():
    config = {"configurable": {"thread_id": "thread-1"}}
    checkpointer = MemorySaver()

    graph = (
        StateGraph(AgentState)
        .add_node("start_node", start_node)
        .add_node("interrupt_node", interrupt_node)
        .add_edge(START, "start_node")
        .add_edge("start_node", "interrupt_node")
        .add_edge("interrupt_node", END)
        .compile(checkpointer=checkpointer)
    )

    result = graph.invoke({"messages": "I am junius."}, config=config)
    print("=" * 50)
    print_interrupt_in_result(result)
    print("=" * 50)

    # resume the graph from the interrupt node
    result = graph.invoke(Command(resume="I am sick today"), config=config)
    print(result)


def sequential_interrupt_graph():

    def node1_handler(state: AgentState) -> AgentState:
        """First node that creates an interrupt"""
        approved = interrupt({"type": "approval", "message": "Do you approve step 1?"})
        return {"messages": state["messages"] + f" | Step 1 approved: {approved}"}

    def node2_handler(state: AgentState) -> AgentState:
        """Second node that creates an interrupt"""
        approved = interrupt(
            {"type": "verification", "message": "Please verify step 2"}
        )
        return {"messages": state["messages"] + f" | Step 2 verified: {approved}"}

    def node3_handler(state: AgentState) -> AgentState:
        """Third node that creates an interrupt"""
        approved = interrupt({"type": "confirmation", "message": "Confirm step 3?"})
        return {"messages": state["messages"] + f" | Step 3 confirmed: {approved}"}

    # Create a graph with multiple nodes that can interrupt
    multi_interrupt_graph = (
        StateGraph(AgentState)
        .add_node("node1", node1_handler)
        .add_node("node2", node2_handler)
        .add_node("node3", node3_handler)
        .add_edge(START, "node1")
        .add_edge("node1", "node2")
        .add_edge("node2", "node3")
        .add_edge("node3", END)
        .compile()
    )
    result = multi_interrupt_graph.invoke({"messages": "Starting multi-step process."})
    print_interrupt_in_result(result)


def multi_interrupt_node(state: AgentState) -> AgentState:

    def multi_interrupt_node(state: AgentState) -> AgentState:
        """A node that creates multiple interrupts sequentially"""
        # First interrupt - approval
        approval = interrupt(
            {"step": 1, "action": "approve", "message": "Approve this action?"}
        )

        # Second interrupt - verification
        verification = interrupt(
            {"step": 2, "action": "verify", "message": "Verify the details?"}
        )

        # Third interrupt - confirmation
        confirmation = interrupt(
            {"step": 3, "action": "confirm", "message": "Confirm completion?"}
        )

        return {
            "messages": state["messages"]
            + f" | Approved: {approval}, Verified: {verification}, Confirmed: {confirmation}"
        }

    single_node_multi_interrupt_graph = (
        StateGraph(AgentState)
        .add_node("multi_interrupt", multi_interrupt_node)
        .add_edge(START, "multi_interrupt")
        .add_edge("multi_interrupt", END)
        .compile()
    )
    result = single_node_multi_interrupt_graph.invoke(
        {"messages": "Testing multiple interrupts."}
    )
    print_interrupt_in_result(result)


def multi_interrupt_graph():
    # Example showing the concept (would need conditional edges or Send for real parallel execution)
    def parallel_node_a(state: AgentState) -> AgentState:
        """Node A that interrupts"""
        approved = interrupt({"node": "A", "message": "Approve from node A?"})
        return {"messages": state["messages"] + f" | Node A: {approved}"}

    def parallel_node_b(state: AgentState) -> AgentState:
        """Node B that interrupts"""
        approved = interrupt({"node": "B", "message": "Approve from node B?"})
        return {"messages": state["messages"] + f" | Node B: {approved}"}

    def parallel_node_c(state: AgentState) -> AgentState:
        """Node C that interrupts"""
        approved = interrupt({"node": "C", "message": "Approve from node C?"})
        return {"messages": state["messages"] + f" | Node C: {approved}"}

    def distributor(state: AgentState):
        """Distributor function that sends to multiple nodes in parallel"""
        # Return a list of Send objects - these nodes will execute IN PARALLEL
        return [
            Send("parallel_node_a", {"messages": state["messages"] + " [A]"}),
            Send("parallel_node_b", {"messages": state["messages"] + " [B]"}),
            Send("parallel_node_c", {"messages": state["messages"] + " [C]"}),
        ]

    def aggregator(state: AgentState) -> AgentState:
        """Aggregator to collect results (won't run if interrupts occur)"""
        return {"messages": state["messages"] + " | Aggregated"}

    # Create graph with TRUE parallel execution
    # Key: Use add_conditional_edges with a function that returns a LIST of Send objects
    parallel_graph = (
        StateGraph(AgentState)
        .add_node("parallel_node_a", parallel_node_a)
        .add_node("parallel_node_b", parallel_node_b)
        .add_node("parallel_node_c", parallel_node_c)
        .add_node("aggregator", aggregator)
        # Conditional edge from START returns list of Send objects - nodes run in parallel
        .add_conditional_edges(
            START, distributor
        )  # Returns [Send(...), Send(...), Send(...)]
        .add_edge("parallel_node_a", "aggregator")
        .add_edge("parallel_node_b", "aggregator")
        .add_edge("parallel_node_c", "aggregator")
        .add_edge("aggregator", END)
        .compile()
    )
    result = parallel_graph.invoke({"messages": "Testing TRUE parallel execution."})
    print_interrupt_in_result(result)


def multi_interrupt_parallel_graph():

    def simple_parallel_node(state: AgentState) -> AgentState:
        """A node that interrupts - will be called multiple times in parallel"""
        # Extract node identifier from messages (we encode it in the distributor)
        if "[Node1]" in state["messages"]:
            node_name = "Node1"
        elif "[Node2]" in state["messages"]:
            node_name = "Node2"
        elif "[Node3]" in state["messages"]:
            node_name = "Node3"
        else:
            node_name = "Unknown"

        approved = interrupt(
            {"node": node_name, "message": f"Approve from {node_name}?"}
        )
        return {"messages": state["messages"] + f" | {node_name}: {approved}"}

    def simple_distributor(state: AgentState):
        """Distribute to multiple nodes in parallel"""
        # Send same state to multiple nodes - they'll run in parallel
        # We'll differentiate them by the order they're called
        return [
            Send("simple_parallel_node", {"messages": state["messages"] + " [Node1]"}),
            Send("simple_parallel_node", {"messages": state["messages"] + " [Node2]"}),
            Send("simple_parallel_node", {"messages": state["messages"] + " [Node3]"}),
        ]

    simple_parallel_graph = (
        StateGraph(AgentState)
        .add_node("simple_parallel_node", simple_parallel_node)
        # Conditional edge directly returns list of Send objects - nodes run in parallel
        .add_conditional_edges(
            START, simple_distributor
        )  # Returns [Send(...), Send(...), Send(...)]
        .add_edge("simple_parallel_node", END)
        .compile()
    )
    result = simple_parallel_graph.invoke({"messages": "Testing parallel execution."})
    print_interrupt_in_result(result)


simple_interrupt_graph()
