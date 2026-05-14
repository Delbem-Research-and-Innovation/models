#!/usr/bin/env bash
# Scaffold a new model under models/<NAME>/.
#
# Usage: make new-model NAME=<snake_case_name>
#
# Creates the four-target Makefile, pyproject.toml (uv, ruff, pyright strict,
# pytest unit marker), src/<NAME>/__init__.py, and tests/conftest.py.

set -euo pipefail

NAME="${1:-}"

if [[ -z "$NAME" ]]; then
  echo "error: NAME is required (e.g. make new-model NAME=my_model)" >&2
  exit 2
fi

if [[ ! "$NAME" =~ ^[a-z][a-z0-9_]*$ ]]; then
  echo "error: NAME must be snake_case (lowercase, digits, underscores), got: $NAME" >&2
  exit 2
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
DEST="$REPO_ROOT/models/$NAME"

if [[ -e "$DEST" ]]; then
  echo "error: $DEST already exists" >&2
  exit 1
fi

mkdir -p "$DEST/src/$NAME" "$DEST/tests"

cat > "$DEST/Makefile" <<'EOF'
.PHONY: dev check test clean

dev:
	uv sync --group dev

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run pyright src tests

test:
	uv run pytest -v || [ $$? -eq 5 ]

clean:
	rm -rf .venv .coverage dist
EOF

cat > "$DEST/pyproject.toml" <<EOF
[project]
name = "$NAME"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = ["ruff>=0.9", "pyright>=1.1", "pytest>=8", "pytest-cov>=6"]

[tool.ruff]
line-length = 100s
exclude = [".venv", "dist", "__pycache__"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
markers = ["unit: fast isolated unit tests"]
EOF

cat > "$DEST/pyrightconfig.json" <<'EOF'
{
  "include": ["src", "tests"],
  "extraPaths": ["src"],
  "venvPath": ".",
  "venv": ".venv",
  "pythonVersion": "3.12",
  "typeCheckingMode": "strict"
}
EOF

touch "$DEST/src/$NAME/__init__.py"

cat > "$DEST/tests/conftest.py" <<'EOF'
# Shared fixtures for this model's tests.
EOF

# Register the model in root pyrightconfig.json so Pylance resolves its imports.
python3 -c "
import json, pathlib
cfg_path = pathlib.Path('$REPO_ROOT/pyrightconfig.json')
cfg = json.loads(cfg_path.read_text())
envs = cfg.setdefault('executionEnvironments', [])
entry = {
    'root': 'models/$NAME',
    'extraPaths': [
        'models/$NAME/src',
        'models/$NAME/.venv/lib/python3.12/site-packages',
    ],
}
if not any(e.get('root') == entry['root'] for e in envs):
    envs.append(entry)
    cfg_path.write_text(json.dumps(cfg, indent=2) + '\n')
"

echo "created: models/$NAME"
echo "next:    cd models/$NAME && make dev && make check && make test"
