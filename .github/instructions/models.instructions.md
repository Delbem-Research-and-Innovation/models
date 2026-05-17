---
applyTo: 'models/**'
description: 'Principles for structuring a model'
---

# Model Conventions

## Principles

Models differ in scope — these principles scale with them. `tests/` layout and CLI are the only fixed rules; everything else follows from the principles. `docs/PROBLEM.md` is the optional home for domain framing (PT-BR allowed).

### 1. Cohesion — one reason to change

Group by what forces change together; the reason becomes the name. Two unrelated reasons-to-change in one artifact → split. Two artifacts that always change together → merge.

### 2. Names carry the contract

Domain nouns name modules; verbs name functions. Generic names (`utils`, `helpers`, `common`, `core`, `lib`, `services`, `internal`, `misc`) signal a missing domain concept.

### 3. The public surface is a liability

Every exported symbol becomes load-bearing once a caller depends on it (Hyrum's Law). Expose the minimum; leave everything else internal. A passive `__init__.py` (see general conventions) lets internals be reorganized freely.

### 4. Types make invariants enforceable

Frozen dataclasses, `Protocol`s, and `NewType` express constraints the type-checker enforces. Prefer unrepresentable illegal states over post-construction validation. Shared types live in `types.py`, created on the second shared use; single-module types live next to their module.

### 5. Functional core, imperative shell

Pure functions at the center; I/O, external calls, and side effects at named boundaries. The boundary validates and translates; the core assumes valid input.

### 6. Dependencies flow toward stability

`types` ← `logic` ← `orchestration` ← `shell`. Stable artifacts imported by less stable ones, never the reverse. No cycles — a cycle signals two artifacts should merge or a third concept is missing between them.

### 7. Defer structure until pain

Flat beats premature hierarchy; duplication beats the wrong abstraction. Split a file when reading it costs more than scanning two would. Add a subpackage when the flat list itself is the cognitive load, not because more files might come. Extract an abstraction on the third instance, not the first.

## Fixed: tests layout

Fixed because pytest discovery, markers, and fixtures depend on it.

```
models/<name>/
└── tests/
    ├── conftest.py             # shared fixtures
    ├── test_<feature>.py       # one file per behavior cluster
    └── <subdir>/               # mirror src/ subpackages only when src/ has them
```

- Every test file: `test_<feature>.py`. Every test function:
  `test_<behavior_under_condition>` — reads as a sentence.
- Fixtures shared across files go in `conftest.py`. Fixtures used by one
  file stay in that file.
- The placeholder `tests/test_example.py` from `make new-model` is deleted
  before the first real commit.

## CLI

When a model has a CLI, it lives in `src/<pkg>/cli/` — always.

```
src/<pkg>/cli/
├── __init__.py       # app = typer.Typer(); registers subcommands
├── <command_a>.py    # @app.command() → calls domain functions
└── <command_b>.py
```

**Typer** is the standard CLI library (`uv add typer`). It derives commands,
flags, validation, and `--help` from type annotations — the same annotations
already required by `pyright strict`. Each command module is a thin binding:
parse and delegate to importable domain functions. No business logic in
`cli/`. The exception to the passive-`__init__.py` rule: `cli/__init__.py`
registers Typer subcommands — that is its only job.

```python
# src/<pkg>/cli/__init__.py
import typer
from <pkg>.cli import train, evaluate

app = typer.Typer()
app.add_typer(train.app, name="train")
app.add_typer(evaluate.app, name="evaluate")
```

Declare the entry point in `pyproject.toml`:

```toml
[project.scripts]
<name> = "<pkg>.cli:app"
```

Models with no CLI do not install Typer.

## Hard nos

- Logic, I/O, or side effects inside `__init__.py`.
- Re-exports from `__init__.py` without explicit `__all__`.
- Module or subpackage named for a role (`utils`, `helpers`, `core`,
  `services`, `internal`, `lib`, `misc`).
- Import cycles between modules of the same model.
- `README.md` per model.
