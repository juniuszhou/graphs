"""Example LangChain agent backed by tools from multiple MCP servers.

Connects a stdio math server and an HTTP weather server via
:class:`~langchain_mcp_adapters.client.MultiServerMCPClient`, loads their
tools, and invokes the agent twice for demo prompts.
"""

import asyncio
import sys
from pathlib import Path
from pprint import pprint

from langchain.agents import create_agent
from langchain_core.messages import ToolMessage

# from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm


async def main() -> None:
    """Load MCP tools, build an agent, and print sample math and weather responses."""
    client = MultiServerMCPClient({
        "math": {
            "transport": "http",  # Local subprocess communication
            "url": "http://localhost:8000/mcp",
        },
        # "weather": {
        #     "transport": "http",  # HTTP-based remote server
        #     # Ensure you start your weather server on port 8000
        #     "url": "http://localhost:8001/mcp",
        # },
    })

    tools = await client.get_tools()

    # Use the session to load tools, resources, or prompts
    # session can include some information about the server, such as the name of the server, the url of the server, the transport of the server, etc.
    # the mcp client will be stateless if you don't pass the session.
    # async with client.session("server_name") as session:
    # Pass the session to load tools, resources, or prompts
    # tools = await load_mcp_tools(session)

    agent = create_agent(
        model=gemma_llm,
        tools=tools,
        system_prompt=(
            "You are a helpful assistant. Use the send_email tool when the user asks "
            "you to send an email."
        ),
    )

    math_response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]
    })
    # weather_response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    # )

    pprint(math_response)

    for message in math_response["messages"]:
        if isinstance(message, ToolMessage):
            print(message.content)  # noqa: T201
    # pprint(weather_response)


if __name__ == "__main__":
    asyncio.run(main())
