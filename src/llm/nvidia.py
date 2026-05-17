"""Simple agent."""

import logging
import sys
from pathlib import Path

import instructor
from langchain.agents import create_agent
from openai import OpenAI
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import (
    nvidia_llm,
    nvidia_model,
    nvidia_nim_api_base,
    nvidia_nim_api_key,
)


class Person(BaseModel):
    """User information include name and age."""

    name: str
    age: int
    city: str
    college: str
    profession: str


agent = create_agent(
    model=nvidia_llm,
    tools=[],
    system_prompt="You are a helpful assistant",
)


def main():
    """Call main function."""
    message = "What is the capital of France?"
    logging.warning(f"Message: {message}")
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    messages = result["messages"]
    for message in messages:
        logging.warning("-" * 100)
        logging.warning(f"Message: {message.content}")


def main_instruct():
    """Call main function."""
    client = instructor.from_openai(
        OpenAI(base_url=nvidia_nim_api_base, api_key=nvidia_nim_api_key)
    )
    message = "Who is Donald Trump?"
    response = client.chat.completions.create(
        model=nvidia_model,
        response_model=Person,
        messages=[{"role": "user", "content": message}],
    )
    for item in response:
        logging.warning("-" * 100)
        logging.warning(f"{item}")


if __name__ == "__main__":
    main_instruct()
