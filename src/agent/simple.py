import os
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import llm

# Set up local LLM (Ollama endpoint)
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"  # Dummy key; Ollama doesn't need a real one

# Initialize LLM with local Ollama service
# llm = ChatOpenAI(
#     model="llama3.2:3b",
#     temperature=0,
#     base_url="http://localhost:11434/v1",
#     api_key="ollama",
# )

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="You are a helpful assistant",
)


