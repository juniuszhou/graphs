import sys
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm


# Context could be used as global data store for application.
@dataclass
class Context:
    user_name: str

@tool
def fetch_user_email_preferences(runtime: ToolRuntime[Context]) -> str:
    """Fetch the user's email preferences from the store."""
    user_name = runtime.context.user_name
    print(f"fetching user email preferences for {user_name}")
    return "The user prefers you to write a brief and polite email."

    

agent = create_agent(
    model=gemma_llm,
    tools=[fetch_user_email_preferences],
    
    system_prompt=(
        "You are a helpful assistant. Use the send_email tool when the user asks "
        "you to send an email."
    ),
    context_schema=Context,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "fetch my email "}]},
    context=Context(user_name="John Doe"),
)

pprint(result)