# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Build / Run**: `langgraph dev` starts the development server for LangGraph. This command hot-reloads changes from `src/`.
- **Lint**: `ruff check .` runs static analysis; `ruff format .` formats code.
- **Test**: `pytest` runs unit tests; to run a single test use `pytest -k <test_name>`.
- **Install**: `pip install -e . "langgraph-cli[inmem]"` installs the package in editable mode with CLI extras.

## Architecture Overview

- Core logic resides in `src/agent/graph.py`, defining the graph structure using LangGraph.
- The `src/utils/` module provides helper functions.
- Additional experimental structures are under `src/deep/` for deep agent implementations.
- Configuration is managed via `.env` files; see `README.md` for environment variable setup.

## Development Workflow

1. Clone the repo and install dependencies.
2. Create a `.env` file from `.env.example` if secrets are needed.
3. Run `langgraph dev` to start the server.
4. Submit changes; the server auto-reloads.
5. Run tests with `pytest` to verify.

## Testing

- Tests are located in the `tests/` directory.
- To run a specific test: `pytest -k test_name`.
- Ensure all new functionality includes appropriate tests.

## Dependencies

- Management via `pyproject.toml`.
- Main dependencies: `langgraph`, `langchain`, `deepagents`, `tavily`, etc.
- Development dependencies: `pytest`, `mypy`, `ruff`.
