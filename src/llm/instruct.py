"""Simple agent."""

import logging
import sys
from pathlib import Path

import instructor
from langchain.agents import create_agent
from openai import OpenAI
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm


class User(BaseModel):
    """User information include name and age."""

    name: str
    age: int


agent = create_agent(
    model=gemma_llm,
    tools=[],
    system_prompt="You are a helpful assistant",
)


def main():
    """Call main function."""
    client = instructor.from_openai(
        OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    )
    message = "What is the capital of France?"
    logging.warning(f"Message: {message}")

    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    messages = result["messages"]
    for message in messages:
        logging.warning("-" * 100)
        logging.warning(f"Message: {message.content}")

    response = client.chat.completions.create(
        model=gemma_llm.model_name,
        response_model=User,
        messages=[{"role": "user", "content": "Tom is 18 years old"}],
    )
    logging.warning(f"Response: {response}")


if __name__ == "__main__":
    main()
