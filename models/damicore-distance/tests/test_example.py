import pytest


@pytest.mark.unit
def test_placeholder() -> None:
    """Placeholder — replace with real tests."""
    assert True


@pytest.mark.unit
def test_with_fixture(sample_texts: tuple[str, str]) -> None:
    """Example using a fixture from conftest."""
    a, b = sample_texts
    assert a != b
