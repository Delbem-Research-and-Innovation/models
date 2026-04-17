import pytest


@pytest.fixture
def sample_text() -> str:
    """Provide a sample raw text for normalization tests."""
    return "  Hello,  World!  "
