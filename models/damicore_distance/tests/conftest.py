import pytest


@pytest.fixture
def sample_texts() -> tuple[str, str]:
    """Provide a pair of texts for distance tests."""
    return ("hello world", "hello earth")
