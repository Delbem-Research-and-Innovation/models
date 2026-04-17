import pytest


@pytest.fixture
def sample_nodes() -> list[str]:
    """Provide sample node labels for tree builder tests."""
    return ["A", "B", "C"]
