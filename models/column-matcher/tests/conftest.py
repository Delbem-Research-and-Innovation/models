import pytest


@pytest.fixture
def sample_record() -> dict[str, str]:
    """Provide a sample record for entity resolution tests."""
    return {"name": "John Doe", "email": "john@example.com"}
