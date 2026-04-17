# models

Monorepo of research models. Each directory under `models/` is an independent Python package; `packages/` contains shared infrastructure.

## Setup

Requires `uv` and `pre-commit` on your machine.

```bash
make install
```

Installs dependencies for every package/model, registers git hooks, and installs [Tectonic](https://tectonic-typesetting.github.io) (LaTeX engine) if not present.

## Working in a model

Each model is self-contained. From a model directory:

```bash
make dev     # install dependencies
make check   # ruff lint + format check + pyright
make test    # pytest
make clean   # remove .venv, dist, coverage
```

Add dependencies via `uv add <package>` and dev dependencies via `uv add --group dev <package>`.

## Creating a new model

Copy an existing model, update `pyproject.toml`, and add a `Makefile`. The root `Makefile` auto-discovers any directory under `models/` that contains a `Makefile`.

## Writing a paper

Each model can have a `paper/` directory with a standalone LaTeX manuscript.

Scaffold:

```bash
make -C packages/research-paper new-paper MODEL=<model-name>
```

Build locally:

```bash
cd models/<model-name>/paper
make paper        # → main.pdf
make paper-clean  # remove build artefacts
```

Shared `.cls` and `.sty` files live in `packages/research-paper/latex/` and are resolved automatically — nothing needs to be copied into the model. Tectonic fetches missing LaTeX packages on the first build and caches them.

CI compiles every changed paper on each PR and publishes the PDF as a build artefact.
