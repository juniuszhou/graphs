"""Simple agent."""

import asyncio
import logging
import sys
from pathlib import Path

from langchain.agents import create_agent

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import llm

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="You are a helpful assistant",
)


async def main():
    """Run the agent asynchronously."""
    user = {"messages": [{"role": "user", "content": "What is the capital of France?"}]}
    # For a single run + events, use only astream_events (ainvoke + astream_events would run twice).
    async for event in agent.astream_events(user):
        logging.warning(event)


if __name__ == "__main__":
    asyncio.run(main())
