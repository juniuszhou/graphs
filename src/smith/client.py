from langsmith import Client
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LANGSMITH_API_KEY")
client = Client(api_key=api_key)

# list runs
runs = client.list_runs(project_name="langsmith-trace-demo")
for run in runs:
    print(run.id)
    print(run.name)
    print(run.status)
    print(run.start_time)
    print(run.end_time)
    print(run.error)
    print(run.metadata)