"""LLM utilities."""

import os

import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# Set up local LLM (Ollama endpoint)
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"  # Dummy key; Ollama doesn't need a real one

nvidia_nim_api_key = os.environ["NVIDIA_NIM_API_KEY"]
nvidia_nim_api_base = "https://integrate.api.nvidia.com/v1"
nvidia_model = "google/gemma-3n-e2b-it"

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

nvidia_llm = ChatOpenAI(
    # model="nvidia/nemotron-3-super-120b-a12b",
    model="google/gemma-3n-e2b-it",
    temperature=0,
    base_url=nvidia_nim_api_base,
    api_key=nvidia_nim_api_key,
)
