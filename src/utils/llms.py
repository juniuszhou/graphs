import os
from langchain_openai import ChatOpenAI

# Set up local LLM (Ollama endpoint)
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"  # Dummy key; Ollama doesn't need a real one

# Initialize LLM with local Ollama service
llm = ChatOpenAI(
    model="llama3.2:3b",
    temperature=0,
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

gemma_llm = ChatOpenAI(
    model="gemma4:e2b",
    temperature=0,
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)