.PHONY: dev check test clean

export PYRIGHT_PYTHON_FORCE_VERSION := latest

dev:
	uv sync --group dev

check:
	uv run ruff check --fix .
	uv run ruff format .
	uv run pyright src tests

test:
	uv run pytest -v || [ $$? -eq 5 ]

clean:
	rm -rf .venv .coverage dist
