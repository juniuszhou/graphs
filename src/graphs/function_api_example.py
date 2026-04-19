from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.types import interrupt
import time

# import asyncio
import concurrent.futures


@task
def write_essay(topic: str) -> str:
    """Write an essay about the given topic."""
    time.sleep(1)  # A placeholder for a long-running task.
    return f"An essay about topic: {topic}"


@task
def task_one(topic: str) -> str:
    """Write an essay about the given topic."""
    time.sleep(1)  # A placeholder for a long-running task.
    return f"An essay about topic: {topic}"


@task
def task_two(topic: str) -> str:
    """Write an essay about the given topic."""
    time.sleep(1)  # A placeholder for a long-running task.
    return f"An essay about topic: {topic}"


@entrypoint(checkpointer=InMemorySaver())
def workflow(topic: str) -> dict:
    """A simple workflow that writes an essay and asks for a review."""
    # use result to get the value from task
    essay = write_essay("cat").result()

    # must use asyncio.gather to get the value from task
    # a, b = asyncio.gather(task_one("cat"), task_two("dog"))
    # print(a, b)

    return {
        "essay": essay,  # The essay that was generated
        "is_approved": True,  # Response from HIL
    }


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "some_thread_id"}}
    result = workflow.invoke({"topic": "cats"}, config=config)
    print(result)
