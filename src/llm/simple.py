"""Simple agent."""

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
