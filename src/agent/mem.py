"""Simple agent."""

import logging
import sys
from pathlib import Path

from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore
from langmem import (
    create_manage_memory_tool,
    create_memory_manager,
    create_prompt_optimizer,
    create_search_memory_tool,
)
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import nvidia_llm, nvidia_model


class Episode(BaseModel):
    """Capture successful reasoning chains."""

    observation: str
    thoughts: str
    action: str
    result: str


store = InMemoryStore(
    index={
        "dims": 1536,  # embedding dimension
        "embed": "openai:text-embedding-3-small",  # or other provider
    }
)

manage_tool = create_manage_memory_tool(namespace=("memories",), schema=Episode)
search_tool = create_search_memory_tool(namespace=("memories",))


# ========================== 2. Semantic Memory
class UserFact(BaseModel):
    """User facts and preferences."""

    key: str = Field(..., description="简短标识，如 user_name, theme, location")
    value: str
    confidence: float = 1.0


semantic_manager = create_memory_manager(
    nvidia_model,
    schemas=[UserFact],
    instructions="Extract important user facts, preferences, and personal information.",
    enable_inserts=True,
    enable_updates=True,
)

semantic_manage_tool = create_manage_memory_tool(
    namespace=("user", "junius", "facts"),  # 多用户时建议带 user_id
    store=store,
)
semantic_search_tool = create_search_memory_tool(
    namespace=("user", "junius", "facts"), store=store
)


# ========================== 3. Episodic Memory
class Episode(BaseModel):
    """Episodic memory: specific experiences."""

    date: str
    observation: str
    action_taken: str
    outcome: str
    success: bool
    lesson: str | None = None


episodic_manager = create_memory_manager(
    nvidia_model,
    schemas=[Episode],
    instructions="Extract meaningful interaction episodes with clear lessons learned.",
    enable_inserts=True,
)

episodic_search_tool = create_search_memory_tool(
    namespace=("user", "junius", "episodes"), store=store
)

# 4 Procedural Memory
prompt_optimizer = create_prompt_optimizer(
    nvidia_model,
    kind="metaprompt",  # 或 "instructions"
)

# create agent
agent = create_agent(
    model=nvidia_llm,
    tools=[
        semantic_manage_tool,
        semantic_search_tool,
        episodic_manager,
        episodic_search_tool,
        prompt_optimizer,
    ],
    system_prompt="You are a helpful assistant",
)


def run_with_memory(user_message: str, conversation_history: list):
    """Run the agent with memory."""
    # Step 1: 检索记忆
    semantic_mem = store.search(
        ("user", "junius", "facts"), query=user_message, limit=5
    )
    for item in semantic_mem:
        logging.warning(item)
    episodic_mem = store.search(
        ("user", "junius", "episodes"), query=user_message, limit=3
    )
    for item in episodic_mem:
        logging.warning(item)

    # Step 2: 构建增强提示（注入三种记忆）
    enhanced_system = store.search(("memories",), query=user_message, limit=10)
    for item in enhanced_system:
        logging.warning(item)

    semantic_manager.invoke(user_message)
    episodic_manager.invoke(user_message)
