import pytest


@pytest.fixture
def sample_map_options() -> list[str]:
    """Provide sample map options for selector tests."""
    return ["map_a", "map_b", "map_c"]
