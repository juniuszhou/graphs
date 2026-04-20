from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llms import llm
from agent.pack import pack

print(pack(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]))

# agent = create_agent(model=llm)

# result = agent.invoke(
#     {
#         "input": "What is the capital of France?",
#         "messages": [HumanMessage(content="What is the capital of France?")],
#     }
# )
# print(result["messages"])
# print("="*50)
# results = agent.batch(
#     [
#         {
#             "input": "What is the capital of France?",
#             "messages": [HumanMessage(content="What is the capital of France?")],
#         },
#         {
#             "input": "What is the capital of France?",
#             "messages": [HumanMessage(content="What is the capital of France?")],
#         },
#     ]
# )
# for result in results:
#     print(result["messages"])
# print("="*50)

# results = agent.stream(
#     {
#             "input": "What is the capital of France?",
#             "messages": [HumanMessage(content="What is the capital of France?")],
#         },
# )
# for result in results:
#     print(result)