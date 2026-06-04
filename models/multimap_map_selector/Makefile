.PHONY: dev check test clean

export PYRIGHT_PYTHON_FORCE_VERSION := latest

dev:
	uv sync --group dev

check:
	uv run ruff check .
		uv run ruff format --check .
	uv run pyright src tests

test:
	uv run pytest -v || [ $$? -eq 5 ]

run:
	python3 -m multimap_map_selector.cli --input . --output test_results_cli --batch

clean:
	rm -rf .venv .coverage dist
