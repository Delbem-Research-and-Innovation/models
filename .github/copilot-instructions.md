# Copilot Instructions

Python research monorepo. `models/*` are independent uv projects; `packages/*` are shared infra. **Trust these instructions; search the codebase only if something here is incomplete or contradicted by reality.**

Code conventions (function shape, types, docstrings, tests, errors) live in [`.github/instructions/general.instructions.md`](./instructions/general.instructions.md).
This file covers orientation, build/validate workflow, and commit rules only.

## Stack

- **Python 3.12** (`requires-python = ">=3.12"`).
- **uv** for env + deps (`uv sync`, `uv add`, `uv run`).
- **ruff** lint + format.
- **pyright strict** mode.
- **pytest**.
- **Tectonic** for LaTeX papers.
- **Make** is the only entry point. Never call `uv` / `pytest` / `ruff` directly when a Makefile target exists.

## Layout

```
models/<name>/             # independent uv project; internal layout → general.instructions.md
models/fixtures/           # shared sample datasets
packages/<name>/           # shared infra; same Makefile contract
  api/  postgresdb/  research-paper/
.github/workflows/         # pr.yml (change-detected matrix), papers.yml, build-paper.yml
pyrightconfig.json         # root: execution environments for cross-package types
```

The root `Makefile` auto-discovers every `models/*/Makefile` and `packages/*/Makefile`.

## Makefile contract (required interface, every package)

| Target  | Does                                                 |
| ------- | ---------------------------------------------------- |
| `dev`   | `uv sync --group dev` (idempotent)                   |
| `check` | `ruff check .` + `ruff format --check .` + `pyright` |
| `test`  | `uv run pytest -v` (exit 5 = no tests is OK)         |
| `clean` | remove `.venv`, `dist`, `.coverage`                  |

Do not invent new targets. CI fans these out across changed packages only.

## Workflow

1. **Work inside one package.** `cd models/<name>` (or `packages/<name>`) before any command. The repo-root `make` aggregators are for fan-out only.
2. **Validate before declaring done:** run `make check && make test` inside every touched package. If you change `packages/postgresdb`, also run its dependents (`packages/api`, etc.).
3. **Scaffold new models** via `make new-model NAME=<snake_case>` from repo root — never create directories by hand. This updates the root `pyrightconfig.json` automatically.
4. **Scaffold papers** via `make -C packages/research-paper new-paper MODEL=<name>`.
5. **Pre-commit** auto-fixes ruff/format/whitespace and blocks broken YAML/TOML, merge conflicts, files > 2 MB, and private keys. If a hook rewrites files, `git add -u` and commit again.
6. **CI** (`pr.yml`) diffs against base, matrix-builds only changed packages.
   Root infra changes (`Makefile`, `pyrightconfig.json`, `.python-version`) and
   shared fixture changes (`models/fixtures/`) trigger all packages. Dependency
   propagation is built in (`postgresdb` → `api`). A fixed-name `gate` job
   aggregates the matrix for branch protection.

## Where new code goes

| Adding… | Put it in |
| :--- | :--- |
| A new model / algorithm | `make new-model NAME=<snake_case>` |
| Infra used by ≥2 models | `packages/<name>/`, then update root `pyrightconfig.json` |
| Sample data shared across models | `models/fixtures/` |
| A LaTeX paper for a model | `models/<model>/paper/` via `make new-paper` |

## Issues as source of truth

Model intent (inputs, outputs, business rules, non-goals) lives in GitHub issues, not in repo files. Honour stated non-goals — no speculative features (YAGNI).

## Commits

Conventional commits, English, present tense, one logical change per commit:

```
feat(column-matcher): add fuzzy threshold validation
fix(api): handle empty response from postgres query
test(damicore-distance): cover NCD edge cases
refactor(postgresdb): extract connection helper
```

Use the normal tool flow (`report_progress`) for commits. Do not invent branches or force-push.

## Hard don'ts

- Don't create Markdown docs unless the user asks. Code, NumPy docstrings, and `docs/PROBLEM.md` are the contract.
- Don't remove working code unless fixing a verified bug or security issue.
- Don't commit secrets, credentials, or API keys.
- Don't add `TODO`, `FIXME`, or commented-out code.

## Out-of-scope improvements

If you spot a problem outside the requested task (missing test, stale dep, refactor opportunity), open a GitHub issue instead of expanding scope.

## Writing — Basis Form

Produce any artifact, and read any prompt, as a basis of its decision space — not an enumeration of cases.

Vocabulary (do not paraphrase):

- Basis: a statement that is an axis of the decision space, not a point. The reader expands it to the cases.
- Span: the set of concrete decisions derivable by combining the statements.
- Irreducible: removing it shrinks the span; no combination of the others recovers it.
- Orthogonal: statements share no content; removing one does not change what the other covers.

Modes:

- Verbose: enumerates; restates in new words.
- Vague: abstract but empty ("be consistent").
- Cryptic: dense but undecodable without context.
- Dense (target): few statements, irreducible and orthogonal across the span.

Input protocol (before any non-trivial answer):

- Artifact: what shape must the output take?
- Axes: derive 3–7 axes native to this artifact's decision space.
- Real question: which decision must this answer close?
  If any is ambiguous, ask one clarifying question; do not answer with hedges.

Output audit (before delivering):

- Redundancy: can a combination of the others imply this? If yes → delete.
- Load-bearing: does removing it lose any concrete decision? If no → delete.
- Class vs. case: class or single case? If single → demote to an example under a basis statement.

Anti-signature: any statement longer than one line signals wrong basis — re-pick axes.
