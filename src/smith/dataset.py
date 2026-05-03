from datasets import load_dataset
from langsmith import Client
from langsmith import traceable
from langsmith.evaluation import evaluate

client = Client()

dataset = client.create_dataset("gsm8k-mini")

hf_ds = load_dataset("gsm8k", "main", split="test[:20]")

for row in hf_ds:
    client.create_example(
        inputs={"question": row["question"]},
        outputs={"answer": row["answer"]},
        dataset_id=dataset.id,
    )



@traceable
def my_app(inputs: dict) -> dict:
    question = inputs["question"]

    resp = "hello world"

    return {
        "answer": resp
    }

results = evaluate(
    my_app,
    data="gsm8k-mini",
    evaluators=[gsm8k_evaluator],
    experiment_prefix="gsm8k-test",
)