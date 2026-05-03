import os
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm

agent = create_agent(
    model=gemma_llm,
    tools=[],
    system_prompt="You are a helpful assistant",
)


