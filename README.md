# models

Monorepo of research models. Each directory under `models/` is an independent Python package; `packages/` holds shared infrastructure.

## Linux dev environment setup

Install system dependencies (Debian/Ubuntu):

```bash
sudo apt update && sudo apt install -y build-essential curl git
```

Install `uv` (Python toolchain manager):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env   # or restart the shell
```

Install `pre-commit`:

```bash
uv tool install pre-commit
```

`make` ships with `build-essential` above. Verify the stack:

```bash
uv --version
make --version
pre-commit --version
```

## Prerequisites

`uv` and `pre-commit` on your machine.

## Bootstrap

```bash
make install
```

Installs dependencies for every package, registers git hooks, and installs
[Tectonic](https://tectonic-typesetting.github.io) (LaTeX engine) on demand.

## Daily workflow

Always work inside one model:

```bash
cd models/<name>
make dev     # install dependencies
make check   # ruff + pyright
make test    # pytest
make clean   # remove .venv, dist, .coverage
```

Add dependencies inside that package with `uv add <pkg>` (or `uv add --group dev <pkg>`); never hand-edit `pyproject.toml`.

`pre-commit` auto-fixes ruff/format/whitespace on every commit. `pyright` and
`pytest` are **not** in hooks — run both before every push:

```bash
make check && make test
```

CI blocks the merge if either fails.

## Scaffolding

```bash
make new-model NAME=<snake_case>
```

The root `Makefile` auto-discovers any `models/*/Makefile` and `packages/*/Makefile`, so a new package is picked up by `make install`, `make check`, and `make test` with no extra wiring.

## Building a paper

```bash
make -C packages/research-paper new-paper MODEL=<name>   # scaffold from template

cd models/<name>/paper
make paper        # → main.pdf
make paper-clean
```

Shared `.cls` / `.sty` from `packages/research-paper/latex/` are resolved
automatically. Tectonic fetches and caches missing LaTeX packages on first
build. CI compiles every changed paper on each PR and publishes the PDF as a
build artefact.
