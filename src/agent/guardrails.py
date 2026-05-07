"""Example of using Guardrails to enforce security and compliance.

Guardrails is a library that allows you to enforce security and compliance in your LLM applications.
It is a library that allows you to enforce security and compliance in your LLM applications.
It is a library that allows you to enforce security and compliance in your LLM applications.
"""

import logging
import sys
from pathlib import Path

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm

# before the agent starts, after it completes, or around model and tool calls.

agent = create_agent(
    model=gemma_llm,
    tools=[],
    middleware=[
        # Redact emails in user input before sending to model
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
        ),
        # Mask credit cards in user input
        PIIMiddleware(
            "credit_card",
            strategy="mask",
            apply_to_input=True,
        ),
        # Block API keys - raise error if detected
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",
            apply_to_input=True,
        ),
    ],
    system_prompt=(
        "You are a helpful assistant. Use the send_email tool when the user asks "
        "you to send an email."
    ),
)

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "My email is john.doe@example.com and card is 5105-1051-0510-5100",
        }
    ]
})

logging.info(result)
