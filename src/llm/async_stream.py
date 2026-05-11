"""Simple agent."""

import asyncio
import json
import logging
import sys
from pathlib import Path

from langchain.agents import create_agent

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm

agent = create_agent(
    model=gemma_llm,
    tools=[],
    system_prompt="You are a helpful assistant",
)


async def main():
    """Run the agent asynchronously."""
    message = "What is the capital of France?"
    logging.warning(f"Message: {message}")

    # LangGraph agent input must be state-shaped: a dict with `messages`, not a raw str.
    inputs = {"messages": [{"role": "user", "content": message}]}

    async for event in agent.astream_events(inputs):
        data = json.dumps(event, default=str, indent=2)
        logging.warning(data)
        logging.warning("-" * 100)


if __name__ == "__main__":
    asyncio.run(main())
