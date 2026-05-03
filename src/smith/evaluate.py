from langsmith import Client

client = Client()

dataset = client.create_dataset(
    dataset_name="qa-test-set",
    description="Simple QA evaluation set"
)

client.create_example(
    inputs={"question": "法国首都是哪里？"},
    outputs={"answer": "巴黎"},
    dataset_id=dataset.id,
)

client.create_example(
    inputs={"question": "日本首都是哪里？"},
    outputs={"answer": "东京"},
    dataset_id=dataset.id,
)

