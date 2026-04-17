---
description: "Custom instructions for Monorepo"
applyTo: "**"
---

# Monorepo Development Guidelines

This is a Monorepo project with packages at packages/, strict type checking, and modular architecture. Follow these rules for all code generation.

## For Python Packages

**Python Best Practices:**

- Use type hints for all function parameters and return values
- Prefer f-strings for string formatting over older methods
- Use descriptive variable and function names
- Implement proper error handling with specific exception types
- Use virtual environments for dependency management

### Quick Rules

- Follow PEP 8 style guidelines strictly
- Prefer f-strings for string formatting over older methods
- Use descriptive variable and function names
- Implement proper error handling with specific exception types
- Use virtual environments for dependency management
- **Type hints**: Mandatory on ALL functions and methods
- **Test markers**: Always use @pytest
- **Imports**: stdlib → external → project (ruff auto-sorts)
- **Commits**: Use conventional format (`feat:`, `fix:`, `docs:`)
- **Before done**: Run `make check` and `make test`
- **Language**: ALWAYS write code, comments, docstrings, and commit messages in ENGLISH
- **Well-grounded**: Generate code that is maintainable, not just code that compiles. Follow clean code principles and modern Python patterns.
- **YAGNI (You Aren't Gonna Need It)**: Implement only what is needed now. Avoid speculative features, over-engineered abstractions, and premature generalization. If functionality isn't required don't build it.

### Code Style: Clean Code

**Clean Code Principles:**
- Write self-documenting code with meaningful names
- Keep functions small and focused on a single responsibility
- Avoid deep nesting and complex conditional statements
- Use consistent formatting and indentation
- Write code that tells a story and is easy to understand
- Refactor ruthlessly to eliminate code smells

## Modern Python Patterns

Write code like a pragmatic senior developer. Generate clean, maintainable solutions.

### 1. Prefer Functions Over Classes

```python
# ✅ Simple, testable, composable
def calculate_discount(price: float, rate: float) -> float:
    """Calculate discount."""
    return price * (1 - rate)

# ❌ Over-engineered
class DiscountCalculator:
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def calculate(self, price: float) -> float:
        return price * (1 - self.rate)
```

### 2. Immutability and Pure Functions

```python
# ✅ Pure function, no side effects
def add_item(items: list[str], new_item: str) -> list[str]:
    """Return new list with item added."""
    return [*items, new_item]

# ❌ Mutates input
def add_item(items: list[str], new_item: str) -> None:
    items.append(new_item)
```

### 3. Dataclasses for Data

```python
# ✅ Clean, typed, immutable
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    name: str
    email: str
    age: int

# ❌ Mutable dict or complex class
user = {"name": "John", "email": "john@example.com"}
```

### 4. Composition Over Inheritance

```python
# ✅ Composition
@dataclass
class EmailService:
    sender: str

    def send(self, to: str, message: str) -> None:
        pass

@dataclass
class NotificationSystem:
    email_service: EmailService

    def notify(self, user: str, message: str) -> None:
        self.email_service.send(user, message)

# ❌ Deep inheritance hierarchy
class BaseNotification:
    pass

class EmailNotification(BaseNotification):
    pass
```

### 5. Type Hints Everywhere

```python
# ✅ Complete type information
def process_items(
    items: list[dict[str, int]],
    filter_func: Callable[[dict[str, int]], bool],
) -> list[dict[str, int]]:
    return [item for item in items if filter_func(item)]

# ❌ Any or missing types
def process_items(items, filter_func):
    return [item for item in items if filter_func(item)]
```

### 6. List/Dict Comprehensions

```python
# ✅ Pythonic, readable
valid_items = [item for item in items if item.is_valid()]
squares = {x: x**2 for x in range(10)}

# ❌ Verbose loops
valid_items = []
for item in items:
    if item.is_valid():
        valid_items.append(item)
```

### 7. Pattern Matching (Python 3.10+)

```python
# ✅ Modern, clear intent
def handle_response(response: dict[str, Any]) -> str:
    match response:
        case {"status": "success", "data": data}:
            return f"Success: {data}"
        case {"status": "error", "message": msg}:
            return f"Error: {msg}"
        case _:
            return "Unknown response"

# ❌ Nested if/elif
def handle_response(response: dict[str, Any]) -> str:
    if "status" in response:
        if response["status"] == "success":
            return f"Success: {response['data']}"
        elif response["status"] == "error":
            return f"Error: {response['message']}"
    return "Unknown response"
```

### 8. Explicit Error Handling

```python
# ✅ Specific exceptions, clear messages
def load_config(path: str) -> dict[str, Any]:
    if not path:
        raise ValueError("Config path cannot be empty")

    if not Path(path).exists():
        raise FileNotFoundError(f"Config not found: {path}")

    # Load config...

# ❌ Silent failures or generic exceptions
def load_config(path: str) -> dict[str, Any] | None:
    try:
        # Load config...
    except Exception:
        return None
```

### 9. Protocols for Duck Typing

```python
# ✅ Structural typing
from typing import Protocol

class Serializable(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

def save(obj: Serializable) -> None:
    data = obj.to_dict()
    # Save...

# ❌ Abstract base classes for everything
from abc import ABC, abstractmethod

class Serializable(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass
```

### 10. Context Managers for Resources

```python
# ✅ Automatic cleanup
from contextlib import contextmanager

@contextmanager
def database_connection(url: str):
    conn = connect(url)
    try:
        yield conn
    finally:
        conn.close()

with database_connection("db://localhost") as conn:
    conn.execute("SELECT * FROM users")

# ❌ Manual cleanup
def query_users(url: str) -> list[User]:
    conn = connect(url)
    try:
        result = conn.execute("SELECT * FROM users")
        return result
    finally:
        conn.close()
```

## Code Generation Templates

### Function Template (ALWAYS use this structure)

```python
def process_data(
    items: list[str],
    threshold: float = 0.85,
    validate: bool = True,
) -> dict[str, list[str]]:
    """Process items with threshold.

    Parameters
    ----------
    items : list[str]
        Input items to process.
    threshold : float, optional
        Minimum threshold, by default 0.85.
    validate : bool, optional
        Whether to validate inputs, by default True.

    Returns
    -------
    dict[str, list[str]]
        Processed results grouped by category.

    Raises
    ------
    ValueError
        If items are empty or invalid.
    """
```

### Test Template (ALWAYS use this structure)

```python
import pytest
from project_name.core.processor import process_data


@pytest.mark.unit
def test_process_data_valid_input() -> None:
    """Test process_data with valid input."""
    items = ["a", "b", "c"]
    result = process_data(items, threshold=0.5)

    assert isinstance(result, dict)
    assert len(result) > 0
```

## Anti-patterns to AVOID

```python
# ❌ Missing type hints
def process(data):
    pass

# ❌ Missing docstring
def process(data: list[str]) -> dict:
    return {}

# ❌ Missing test marker
def test_something():
    pass

# ❌ Business logic in CLI
# cli/main.py
def main():
    data = complex_algorithm()  # Wrong! Move to core/

# ❌ Wrong import direction
# core/models.py
from project_name.parsers import parse  # Never import upward!
```

## Python Common Patterns
s
### Error Handling

```python
def process(data: list[str]) -> dict[str, int]:
    """Process data with validation."""
    if not data:
        raise ValueError("Data cannot be empty")

    if not all(isinstance(item, str) for item in data):
        raise TypeError("All items must be strings")

    # Process...
```

### Fixture Usage

```python
# tests/conftest.py
import pytest


@pytest.fixture
def sample_data() -> list[str]:
    """Provide sample data for tests."""
    return ["item1", "item2", "item3"]


# tests/unit/test_feature.py
@pytest.mark.unit
def test_process(sample_data: list[str]) -> None:
    """Test with fixture data."""
    result = process(sample_data)
    assert result is not None
```

## File Naming

- Tests: `test_<feature>.py` or `<feature>_test.py`
- Modules: `<purpose>_<type>.py` (e.g., `csv_parser.py`, `data_models.py`)
- Fixtures: `tests/fixtures/sample_data.json`

## Commands Reference

```bash
make dev           # Setup (run once)
make test-fast     # Quick validation while coding
make check         # Before committing
make test          # Full test suite
```

## Commit Messages

When suggesting commits, use:

```bash
feat: add new feature
fix: resolve bug in parser
docs: update architecture guide
test: add integration tests
refactor: improve code structure
```

## Clean Code & Engineering Practices

Generate code that is maintainable, not just code that compiles.

### YAGNI (You Aren't Gonna Need It)

```python
# ✅ Implement what's needed now
def calculate_total(items: list[float]) -> float:
    """Calculate total of items."""
    return sum(items)

# ❌ Over-engineered for "future needs"
class CalculationEngine:
    def __init__(self, strategy: str = "simple") -> None:
        self.strategy = strategy
        self.cache: dict[str, float] = {}

    def calculate_total(self, items: list[float], mode: str = "default") -> float:
        # Complex logic for scenarios that don't exist yet
        pass
```

### Single Responsibility

```python
# ✅ Each function does one thing
def load_data(path: str) -> str:
    """Load raw data from file."""
    return Path(path).read_text()

def parse_json(content: str) -> dict[str, Any]:
    """Parse JSON string to dict."""
    return json.loads(content)

def validate_schema(data: dict[str, Any]) -> bool:
    """Validate data against schema."""
    return "id" in data and "name" in data

# ❌ Function doing too much
def load_and_process_data(path: str) -> dict[str, Any]:
    content = Path(path).read_text()
    data = json.loads(content)
    if "id" not in data or "name" not in data:
        raise ValueError("Invalid schema")
    # More processing...
    return data
```

### Meaningful Names

```python
# ✅ Clear, descriptive
def calculate_monthly_revenue(transactions: list[Transaction]) -> float:
    """Calculate total revenue for the month."""
    return sum(t.amount for t in transactions if t.type == "income")

# ❌ Cryptic abbreviations
def calc_rev(tx: list) -> float:
    return sum(t.amt for t in tx if t.tp == "inc")
```

### Small Functions

```python
# ✅ Functions under 20 lines
def process_user(user_data: dict[str, Any]) -> User:
    """Create User from raw data."""
    validated = _validate_user_data(user_data)
    normalized = _normalize_user_data(validated)
    return User(**normalized)

def _validate_user_data(data: dict[str, Any]) -> dict[str, Any]:
    """Validate required fields."""
    required = {"name", "email"}
    if not required.issubset(data.keys()):
        raise ValueError(f"Missing fields: {required - data.keys()}")
    return data

# ❌ 100+ line functions
def process_user(user_data: dict[str, Any]) -> User:
    # Validation logic...
    # Normalization logic...
    # Business rules...
    # Side effects...
    # More logic...
    pass
```

### No Magic Numbers

```python
# ✅ Named constants
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30

def fetch_data(url: str) -> str:
    for attempt in range(MAX_RETRY_ATTEMPTS):
        response = requests.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
        if response.ok:
            return response.text
    raise Exception("Failed after retries")

# ❌ Unexplained numbers
def fetch_data(url: str) -> str:
    for attempt in range(3):
        response = requests.get(url, timeout=30)
        if response.ok:
            return response.text
    raise Exception("Failed after retries")
```

### Early Returns

```python
# ✅ Guard clauses, reduced nesting
def process_order(order: Order) -> bool:
    """Process order if valid."""
    if not order.items:
        return False

    if order.total <= 0:
        return False

    if not order.customer.is_active:
        return False

    # Process order...
    return True

# ❌ Deep nesting
def process_order(order: Order) -> bool:
    if order.items:
        if order.total > 0:
            if order.customer.is_active:
                # Process order...
                return True
    return False
```

### No Premature Optimization

```python
# ✅ Clear, correct first
def find_duplicates(items: list[str]) -> set[str]:
    """Find duplicate items in list."""
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return duplicates

# ❌ Optimizing before profiling
def find_duplicates(items: list[str]) -> set[str]:
    # Complex bit manipulation and custom hash tables
    # for "performance" without benchmarking
    pass
```

### No Technical Debt

```python
# ✅ Complete implementation
def export_data(data: list[dict], format: str) -> str:
    """Export data to specified format."""
    match format:
        case "json":
            return json.dumps(data)
        case "csv":
            return _to_csv(data)
        case _:
            raise ValueError(f"Unsupported format: {format}")

# ❌ TODO, FIXME, temporary hacks
def export_data(data: list[dict], format: str) -> str:
    # TODO: implement CSV export
    # FIXME: this is a temporary hack
    return json.dumps(data)  # Always JSON for now
```

### Code Review Mindset

Before generating code, ask:

1. **Is this the simplest solution?** (YAGNI)
2. **Can I understand this in 6 months?** (Readability)
3. **Is each function doing one thing?** (Single Responsibility)
4. **Are the names self-explanatory?** (No mental mapping)
5. **Would this pass code review?** (Standards compliance)

### Red Flags to NEVER Generate

- Functions longer than 50 lines
- Nesting deeper than 3 levels
- Classes with more than 5 methods (consider splitting)
- Missing type hints
- Bare `except:` clauses
- Commented-out code
- TODO/FIXME in production code

## Documentation Rules

**CRITICAL**: Do NOT create markdown documentation files unless explicitly requested.

### What to Document

```python
# ✅ Docstrings for public APIs
def calculate_discount(price: float, rate: float) -> float:
    """Calculate discounted price.

    Parameters
    ----------
    price : float
        Original price.
    rate : float
        Discount rate (0.0 to 1.0).

    Returns
    -------
    float
        Discounted price.
    """
    return price * (1 - rate)
```

### What NOT to Document

```python
# ❌ Do NOT create separate .md files for:
# - Feature explanations (code should be self-explanatory)
# - Implementation notes (use code comments)
# - Change logs (use git commits)
# - API docs (use docstrings)

# ❌ Do NOT write obvious comments
def add(a: int, b: int) -> int:
    # Add two numbers  ← Useless comment
    return a + b

# ❌ Do NOT document internal helpers
def _internal_helper(x: str) -> str:
    # No docstring needed for private functions
    return x.strip().lower()
```

### Documentation Philosophy

- Code is documentation (make it readable)
- Docstrings for public APIs only
- Comments explain WHY, not WHAT
- Avoid over-documentation
- No markdown files for code explanations

## Quality Checklist

Before suggesting code is "done", ensure:

- [ ] Complete type hints on all functions
- [ ] NumPy-style docstrings present
- [ ] Test written with appropriate marker
- [ ] Dead codes removed (no commented-out code)
- [ ] No imports violating dependency rules
- [ ] Code would pass `make check`
- [ ] All linting checks pass (ruff)

## AI Code Generation Preferences

When generating code, please:

- Generate complete, working code examples with proper imports
- Include inline comments for complex logic and business rules
- Follow the established patterns and conventions in this project
- Suggest improvements and alternative approaches when relevant
- Consider performance, security, and maintainability
- Include error handling and edge case considerations
- Generate appropriate unit tests when creating new functions
- Follow accessibility best practices for UI components
