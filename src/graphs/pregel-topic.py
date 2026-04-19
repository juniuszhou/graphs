from langgraph.graph import StateGraph, END
from langgraph.channels import LastValue, Topic
from typing import TypedDict, Annotated


# 定义 state
# class State(dict):
#     result: str


class State(TypedDict):
    # list[str] is for Topic
    # result: Annotated[list[str], LastValue(str)]
    # single value is for LastValue
    result: list[str]
    # result: Annotated[list[str], Topic(str, accumulate=False)]
    final: str


builder = StateGraph(State)


# Node A
def node_a(state):
    return {"result": ["A"]}


# Node B
def node_b(state):
    # print(state)
    return {"result": ["B"]}


def node_c(state):
    print("node_c: ", state)
    result = state["result"]
    return {"result": result}


# 汇总节点
def node_d(state):
    print("node_d: ", state)
    result = state["result"]
    return {"result": result}


builder.add_node("A", node_a)
builder.add_node("B", node_b)
builder.add_node("C", node_c)
builder.add_node("D", node_d)
# 设置 channel
# builder.add_channel("result", Topic(accumulate=False))

builder.set_entry_point("A")
builder.add_edge("A", "C")
builder.add_edge("A", "B")
# builder.add_edge("B", "D")
# builder.add_edge("C", "D")
# builder.add_edge("D", END)

# channel（默认就是 LastValue）
graph = builder.compile()

result = graph.invoke({})
print("Final result: ", result)
