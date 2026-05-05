import sys
from pathlib import Path
from pprint import pprint
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import gemma_llm

SKILLS = [
    {
        "name": "langgraph-expert",
        "description": "用于构建复杂状态机、多代理、持久化流程...",
        "path": "skills/langgraph-expert/SKILL.md"
    },
]

@tool
def load_skill(skill_name: str) -> str:
    """加载指定技能的完整内容（专家指令、最佳实践、模板等）。
    
    仅在需要该领域专业知识时调用。
    """
    for skill in SKILLS:
        if skill["name"] == skill_name:
            try:
                with open(skill["path"], "r", encoding="utf-8") as f:
                    content = f.read()
                return f"【已加载技能】{skill_name}\n\n{content}"
            except Exception as e:
                return f"加载技能失败: {e}"
    
    available = ", ".join(s["name"] for s in SKILLS)
    return f"技能 '{skill_name}' 不存在。可用技能: {available}"

agent = create_agent(
    model=gemma_llm,
    tools=[load_skill],
    system_prompt=(
        "You are a helpful assistant. Use the send_email tool when the user asks "
        "you to send an email."
    ),
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "My email is john.doe@example.com and card is 5105-1051-0510-5100"}]
})

pprint(result)