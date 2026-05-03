import sys
from pathlib import Path

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
    return f"Email sent to {to!r} with subject {subject!r}: {body}"


agent = create_agent(
    model=gemma_llm,
    tools=[send_email],
    middleware=[
        HumanInTheLoopMiddleware(
            # this is the key, middleware can be used before a tool is called
            interrupt_on={
                # Pause before this tool runs so a human can approve, edit, or reject it.
                "send_email": True,
            },
            description_prefix="Tool execution pending approval",
        ),
    ],
    checkpointer=InMemorySaver(),
    system_prompt=(
        "You are a helpful assistant. Use the send_email tool when the user asks "
        "you to send an email."
    ),
)


def print_interrupts(result):
    """Print the review requests returned by HumanInTheLoopMiddleware."""
    interrupts = getattr(result, "interrupts", None)
    if interrupts is None and isinstance(result, dict):
        interrupts = result.get("__interrupt__", [])

    for interrupt in interrupts:
        print(interrupt)


def run_approval_example() -> None:
    """Run an agent until a tool approval interrupt, then approve and resume."""
    config = {"configurable": {"thread_id": "hitl-email-demo"}}

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Send an email to junius@example.com with the subject "
                        "'Hello' and body 'Human approved this message.'"
                    ),
                }
            ]
        },
        config=config,
        version="v2",
    )
    print_interrupts(result)

    human = input("Do you approve of this email? (y/n): ").strip().lower()
    if human == "y":
        result = agent.invoke(
            Command(resume={"decisions": [{"type": "approve"}]}),
            config=config,
            version="v2",
        )
    else:
        result = agent.invoke(
            Command(resume={"decisions": [{"type": "reject"}]}),
            config=config,
            version="v2",
        )

    print(result["messages"][-1].content)


def run_edit_example() -> None:
    """Resume an interrupted tool call with edited tool arguments."""
    config = {"configurable": {"thread_id": "hitl-email-edit-demo"}}

    agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Send junius@example.com a short email about the meeting.",
                }
            ]
        },
        config=config,
        version="v2",
    )

    result = agent.invoke(
        Command(
            resume={
                "decisions": [
                    {
                        "type": "edit",
                        "edited_action": {
                            "name": "send_email",
                            "args": {
                                "to": "junius@example.com",
                                "subject": "Meeting update",
                                "body": "The meeting moved to 3pm.",
                            },
                        },
                    }
                ]
            }
        ),
        config=config,
        version="v2",
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    run_approval_example()
