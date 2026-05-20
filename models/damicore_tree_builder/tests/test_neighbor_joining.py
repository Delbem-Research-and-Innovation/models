import pytest

from damicore_tree_builder.neighbor_joining import NeighborJoining


@pytest.mark.unit
def test_builds_tree_with_expected_node_counts() -> None:
    tree = NeighborJoining(
        ["A", "B", "C", "D"],
        [
            [0.0, 5.0, 9.0, 9.0],
            [5.0, 0.0, 10.0, 10.0],
            [9.0, 10.0, 0.0, 8.0],
            [9.0, 10.0, 8.0, 0.0],
        ],
    ).build_tree()

    assert sorted(clade.name for clade in tree.get_terminals()) == ["A", "B", "C", "D"]
    assert len(tree.get_nonterminals()) == 3


@pytest.mark.unit
def test_requires_at_least_three_elements() -> None:
    with pytest.raises(ValueError, match="at least 3"):
        NeighborJoining(["A", "B"], [[0.0, 1.0], [1.0, 0.0]]).build_tree()
