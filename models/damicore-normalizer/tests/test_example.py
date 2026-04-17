import pytest


@pytest.mark.unit
def test_placeholder() -> None:
    """Placeholder — replace with real tests."""
    assert True


@pytest.mark.unit
def test_with_fixture(sample_text: str) -> None:
    """Example using a fixture from conftest."""
    assert len(sample_text) > 0
