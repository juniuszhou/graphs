import os
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from tavily import TavilyClient

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm

load_dotenv()

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


@tool
def internet_search(
    query: str,
    max_results: int | None = None,
    topic: Literal["general", "news", "finance"] | None = None,
    include_raw_content: bool | None = None,
):
    """Run a web search via Tavily (not the filesystem)."""
    # Local LLMs often send null for optional tool args; coerce before Tavily / validation.
    return tavily_client.search(
        query,
        max_results=max_results if max_results is not None else 5,
        include_raw_content=include_raw_content if include_raw_content is not None else False,
        topic=topic if topic is not None else "general",
    )

# System prompt to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""


# `create_deep_agent` injects many built-in tools (ls, read_file, task, …). Local
# models like llama3.2:3b often mis-bind tool calls (e.g. call `ls` with search args),
# so search fails. Use a single-tool agent here so the only tool is `internet_search`.
agent = create_agent(
    model=gemma_llm,
    tools=[internet_search],
    system_prompt=research_instructions,
)


# result = agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})

# Print the agent's response
# print(result["messages"][-1].content)