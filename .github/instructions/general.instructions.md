---
applyTo: '**'
description: 'Code conventions for Python packages in delbem-research/models'
---

# Code Conventions

## Language

Code, identifiers, docstrings, comments, commits, and test names in **English**.

## Function-first design

Default to functions; use classes only as `@dataclass(frozen=True)` data
containers or `Protocol` implementations.

- **Pure where possible.** No hidden state, no mutation of inputs; return new collections.
- **Small.** ≤ 50 lines, ≤ 3 nesting levels. Module-private helpers prefixed with `_`.
- **One responsibility per function.** Compose.
- **Generators** (`Generator[T, None, None]`) for large datasets, not materialized lists.
- **`@lru_cache`** for pure repeated computations on hashable inputs.

## Type hints

Mandatory on every function and method, including private helpers and tests.
`pyright strict` fails otherwise.

- Built-in generics: `list[str]`, `dict[str, int]`, `tuple[int, ...]`.
- `X | None`, not `Optional[X]`; `X | Y`, not `Union[X, Y]`.
- `Protocol` for structural typing, not ABCs.
- Avoid `Any`. If a third-party lib is untyped (e.g. `thefuzz`), isolate the call with `# type: ignore[<rule>]` on the import line and wrap it in a narrowly typed helper.
- Avoid `cast` unless it documents an invariant the type system can't see.
- Never add `# type: ignore` without a trailing comment explaining why. Never add `# noqa` without the specific rule code.

## Docstrings (NumPy style)

Required on every **public** function (anything not prefixed `_`). Private
helpers only if the name is not self-explanatory. Comments explain **why**, never **what**.

```python
def find_column_matches(
    source_columns: list[str],
    target_columns: list[str],
    threshold: float = 0.8,
) -> list[dict[str, Any]]:
    """One-line summary in the imperative mood.

    Parameters
    ----------
    source_columns : list[str]
        Source-side column names.
    threshold : float, optional
        Minimum similarity (0..1), by default 0.8.

    Returns
    -------
    list[dict[str, Any]]
        Matches with keys ``source``, ``target``, ``score``.

    Raises
    ------
    ValueError
        If ``threshold`` is outside [0, 1].

    Examples
    --------
    >>> find_column_matches(["id"], ["id"])
    [{'source': 'id', 'target': 'id', 'score': 1.0}]
    """
```

## Error handling

Raise specific built-ins (`ValueError`, `TypeError`, `FileNotFoundError`) at
the function boundary, naming the offending value:

```python
if not (0.0 <= threshold <= 1.0):
    raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")
```

- Never bare `except:` or `except Exception:` to log-and-continue.
- Never return `None` to signal an error — raise.
- Validate at the system edge (function entry, file I/O, deserialization). Internal helpers assume validated input.

## Imports

`ruff` sorts and groups them. Rules it does not enforce:

- Absolute imports from the package root: `from column_matcher.matcher import …` (the `src/` layout makes the package name the import root).
- No wildcard imports. No relative imports beyond the same directory.

## Naming

- **Directories and Python packages: `snake_case`**, identical to each other (e.g. `models/column_matcher/src/column_matcher/`). Never kebab-case for importable directories.
- `[project].name` in `pyproject.toml` may use hyphens (PyPI convention); it need not match the import path.
- Modules: `snake_case.py`.
- Test files: `test_<feature>.py`; tests: `test_<behavior_under_condition>` — reads like a sentence.
- Constants: `UPPER_SNAKE_CASE`. Types and dataclasses: `PascalCase`.

## Package layout

```
models/<name>/
├── pyproject.toml
├── pyrightconfig.json
├── Makefile
├── uv.lock
├── docs/                   # optional
├── src/<pkg>/
│   ├── __init__.py
│   └── *.py                # one module per cohesive concept
└── tests/
    ├── conftest.py         # shared fixtures
    └── test_<feature>.py   # mirrors src/
```

`models/*` do not import from each other. Shared code goes in `packages/`, with the cross-package path added to the root `pyrightconfig.json`.

`__init__.py` contains **only** re-exports and `__all__`. No logic, no I/O,
no side effects, no conditional imports. The only acceptable non-import lines
are `__version__ = "..."` or a one-line compatibility shim that cannot live
elsewhere.

```python
# src/<pkg>/__init__.py
from <pkg>.<module> import PublicThing

__all__ = ["PublicThing"]
```

## Testing

- Every test carries a marker. Currently only `@pytest.mark.unit`. Register new markers in `pyproject.toml` (`[tool.pytest.ini_options].markers`).
- Shared fixtures in `tests/conftest.py`. Prefer pure inputs over mocks; mock only at I/O boundaries.
- For every new function cover: happy path, empty/edge inputs, every documented `Raises`, and every non-trivial branch.
- **Assertions are specific and equality-based:**

```python
# ✅
assert similarity_score("Name", "name") == 1.0
assert result == [{"source": "a", "target": "a", "score": 1.0}]
with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
    find_column_matches(["a"], ["a"], threshold=2.0)

# ❌
assert similarity_score("Name", "name")
assert result
```

Existing tests must not be deleted or weakened without justification — fix
the code, not the test.

## Dependencies

- Add with `uv add <pkg>` (runtime) or `uv add --group dev <pkg>` (dev). Never hand-edit `[project].dependencies`.
- Prefer the standard library. Justify each new transitive dependency in the commit message.
- Cross-package deps (e.g. `api` → `postgresdb`) require an `executionEnvironments` entry in the root `pyrightconfig.json`. Each `models/*` stays fully isolated via its own `pyrightconfig.json`.

## Config files — do not relax

Tightening is welcome; loosening requires explicit justification.

## Code review focus

Flag only correctness, test coverage, package boundaries, and strictness
regressions. Skip style nitpicks. Every comment includes a concrete fix.
Leave files with no critical issue untouched.
