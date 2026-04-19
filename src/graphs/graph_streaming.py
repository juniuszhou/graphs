from typing import Annotated, Sequence, TypedDict, Set

import pprint

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from operator import __or__ as or_messages

# You cannot use set[BaseMessage]: messages are unhashable (try hash(HumanMessage(...))).
# For "set-like" behavior — drop redundant updates — use Annotated[..., add_messages]:
# it keeps a list, merges updates from each node, and replaces by message id when ids match.


class State(TypedDict):
    topic: Annotated[Set[str], or_messages]
    joke: str


def add_topic(state: State):
    return {"topic": {"and cats"}}


def generate_joke(state: State):
    # Same id="topic-extra" as add_topic → this row replaces the previous one (no duplicate lines).
    return {
        "topic": {"and cats"},
        "joke": "ok",
    }


checkpointer = InMemorySaver()
graph = (
    StateGraph(State)
    .add_node(add_topic)
    .add_node(generate_joke)
    .add_edge(START, "add_topic")
    .add_edge("add_topic", "generate_joke")
    .add_edge("generate_joke", END)
    .compile(checkpointer=checkpointer)
)

# Same thread_id must be used for invoke/stream and get_state so they refer to one checkpoint.
config = {"configurable": {"thread_id": "demo-thread-1"}}

# The stream() method returns an iterator that yields streamed outputs
# actually they are states of the graph in each node
for chunk in graph.stream(
    {"topic": {"ice cream"}, "joke": ""},
    config=config,
    # Set stream_mode="updates" to stream only the updates to the graph state after each node
    # Other stream modes are also available. See supported stream modes for details
    # other modes are values, messages, updates, custom, checkpoints, tasks, debug
    stream_mode="values",
):
    print("=" * 50)
    pprint.pprint(chunk)
    print()

snapshot = graph.get_state(config)
