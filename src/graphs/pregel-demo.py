from langgraph.channels import EphemeralValue
from langgraph.channels import LastValue
from langgraph.channels import Topic
from langgraph.channels import BinaryOperatorAggregate
from langgraph.pregel import Pregel, NodeBuilder
import operator


def example_one():
    # subscribe_only is used to subscribe to a single channel.
    node1 = NodeBuilder().subscribe_only("a").do(lambda x: x + x).write_to("b")

    app = Pregel(
        nodes={"node1": node1},
        channels={
            "a": EphemeralValue(str),
            "b": EphemeralValue(str),
        },
        input_channels=["a"],
        output_channels=["b"],
    )

    result = app.invoke({"a": "foo"})
    print(result)


def example_two():
    node1 = NodeBuilder().subscribe_only("a").do(lambda x: x + x).write_to("b")

    node2 = NodeBuilder().subscribe_only("b").do(lambda x: x + x).write_to("c")

    app = Pregel(
        nodes={"node1": node1, "node2": node2},
        channels={
            "a": EphemeralValue(str),
            "b": LastValue(str),
            "c": EphemeralValue(str),
            "d": Topic(str, max_concurrency=2),
            "e": BinaryOperatorAggregate(str, operator=operator.concat),
        },
        input_channels=["a"],
        output_channels=["b", "c"],
    )

    app.invoke({"a": "foo"})


def example_topic():
    # subscribe_only is used to subscribe to a single channel.
    node1 = NodeBuilder().subscribe_only("a").do(lambda x: x + x).write_to("b", "c")
    # subscribe_to is used to subscribe to a new channel
    node2 = NodeBuilder().subscribe_to("b").do(lambda x: x["b"] + x["b"]).write_to("c")

    node3 = NodeBuilder().subscribe_to("c").do(lambda x: x["c"]).write_to("d")

    app = Pregel(
        nodes={"node1": node1, "node2": node2, "node3": node3},
        channels={
            "a": EphemeralValue(str),
            "b": EphemeralValue(str),
            # accumulate keep all the values in the channel as list or just keep the last value
            "c": Topic(str, accumulate=False),
            "d": LastValue(str),
        },
        input_channels=["a"],
        output_channels=["d"],
    )

    result = app.invoke({"a": "foo"})
    print(result)


example_topic()
