from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="llama3.2:3b",
    temperature=0,
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

agent = create_agent(model=llm)

result = agent.invoke(
    {
        "input": "What is the capital of France?",
        "messages": [HumanMessage(content="What is the capital of France?")],
    }
)
print(result["messages"])

results = agent.batch(
    [
        {
            "input": "What is the capital of France?",
            "messages": [HumanMessage(content="What is the capital of France?")],
        },
        {
            "input": "What is the capital of France?",
            "messages": [HumanMessage(content="What is the capital of France?")],
        },
    ]
)
for result in results:
    print(result["messages"])

results = agent.stream(
    {
            "input": "What is the capital of France?",
            "messages": [HumanMessage(content="What is the capital of France?")],
        },
)
for result in results:
    print(result)

# simple way to invoke the LLM
result = llm.invoke("What is the capital of France?")
print(result.content)

results = llm.batch(
    ["What is the capital of France?", "What is the capital of Germany?"]
)
for result in results:
    print(result.content)

# stream mode, print each single new output each time
result = llm.stream("What is the capital of France?")
for chunk in result:
    print(chunk.text, end="\n", flush=True)

full = None
# print in full mode
for chunk in result:
    full = chunk if full is None else full + chunk
    print(full.text)
