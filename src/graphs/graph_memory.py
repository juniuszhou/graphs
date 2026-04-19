import uuid
from operator import add as add_messages
from typing import Annotated, NotRequired, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# short term memory
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph

# long term memory
from langgraph.store.memory import InMemoryStore

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


def OnlyNode(state: State) -> State:
    return state


# short memory
checkpointer = InMemorySaver()
graph = (
    StateGraph(State)
    .add_node("OnlyNode", OnlyNode)
    .add_edge(START, "OnlyNode")
    .add_edge("OnlyNode", END)
    .compile(checkpointer=checkpointer)
)

# long term memory
store = InMemoryStore()
graph = (
    StateGraph(State)
    .add_node("OnlyNode", OnlyNode)
    .add_edge(START, "OnlyNode")
    .add_edge("OnlyNode", END)
    .compile(store=store, checkpointer=checkpointer)
)


config = {
    "configurable": {
        "thread_id": uuid.uuid4(),
    }
}

parent_graph = (
    StateGraph(State)
    .add_node("subgraph", graph)
    .add_edge(START, "subgraph")
    .add_edge("subgraph", END)
    .compile(store=store, checkpointer=checkpointer)
)


print(parent_graph.invoke({"topic": "chickens"}, config))


history = list(parent_graph.get_state_history(config))
for state in history:
    print("=" * 50)
    print("Values: ", state.values)
