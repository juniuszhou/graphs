from dotenv import load_dotenv
import uuid
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Annotated, Sequence, NotRequired
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

model = ChatOpenAI(
    model="llama3.2:3b",
    temperature=0,
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


class State(TypedDict):
    topic: NotRequired[str]
    joke: NotRequired[str]


def generate_topic(state: State):
    """LLM call to generate a topic for the joke"""
    msg = model.invoke("Give me a funny topic for a joke")
    return {"topic": msg.content}


def write_joke(state: State):
    """LLM call to write a joke based on the topic"""
    msg = model.invoke(f"Write a short joke about {state['topic']}")
    return {"joke": msg.content}


# Build workflow
workflow = StateGraph(State)

# Add nodes
workflow.add_node("generate_topic", generate_topic)
workflow.add_node("write_joke", write_joke)

# Add edges to connect nodes
workflow.add_edge(START, "generate_topic")
workflow.add_edge("generate_topic", "write_joke")
workflow.add_edge("write_joke", END)

# Compile
checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

config = {
    "configurable": {
        "thread_id": uuid.uuid4(),
    }
}
# invoke without any input
state = graph.invoke({}, config)

print("=" * 50)
print("Topic: ", state["topic"])
print()
print("Joke: ", state["joke"])

states = list(graph.get_state_history(config))

print("=" * 50)
for state in states:
    print(state.next)
    print(state.config["configurable"]["checkpoint_id"])
    print()


print("=" * 50)
selected_state = states[1]
print(selected_state.next)
print(selected_state.values)
print(selected_state.config)

print("=" * 50)
# update the state with a new topic, it is like a time travel. It will start from the selected state and continue from there.
new_config = graph.update_state(selected_state.config, values={"topic": "chickens"})
print(new_config)

print("=" * 50)
result = graph.invoke(None, new_config)
print(result)
