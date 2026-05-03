"""Example: connect a LangChain agent to a public MCP server."""

import asyncio
import sys
from pathlib import Path

DEEPWIKI_MCP_URL = "https://mcp.deepwiki.com/mcp"


def _remove_script_dir_from_path() -> None:
    """Avoid shadowing the upstream `mcp` package with this example file."""
    script_dir = Path(__file__).resolve().parent
    if sys.path and Path(sys.path[0]).resolve() == script_dir:
        sys.path.pop(0)


async def run_deepwiki_agent_example() -> None:
    """Ask DeepWiki's MCP server a question and print the agent response."""
    _remove_script_dir_from_path()

    from langchain.agents import create_agent
    from langchain_mcp_adapters.client import MultiServerMCPClient

    from utils.llms import gemma_llm

    client = MultiServerMCPClient(
        {
            "deepwiki": {
                "url": DEEPWIKI_MCP_URL,
                "transport": "streamable_http",
            }
        }
    )

    tools = await client.get_tools()
    print("Loaded MCP tools:", ", ".join(tool.name for tool in tools))  # noqa: T201

    agent = create_agent(
        model=gemma_llm,
        tools=tools,
        system_prompt=(
            "You are a helpful assistant with access to DeepWiki MCP tools. "
            "Use those tools when answering questions about GitHub repositories."
        ),
    )

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Use DeepWiki to answer this: What is LangChain, and what "
                        "are its main building blocks? Use repo langchain-ai/langchain."
                    ),
                }
            ]
        }
    )

    print(result["messages"][-1].content)  # noqa: T201


if __name__ == "__main__":
    asyncio.run(run_deepwiki_agent_example())
