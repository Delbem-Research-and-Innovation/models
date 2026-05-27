from pathlib import Path

import pytest

from damicore_tree_builder.functional import (
    TreeNode,
    build_neighbor_joining_tree,
    get_nonterminals,
    get_terminals,
    load_distance_matrix,
    run,
    to_newick,
    write_newick,
)


@pytest.mark.unit
def test_load_distance_matrix_valid(tmp_path: Path) -> None:
    matrix_path = tmp_path / "matrix.csv"
    matrix_path.write_text(
        ",A,B,C\nA,0,5,9\nB,5,0,10\nC,9,10,0\n",
        encoding="utf-8",
    )

    names, matrix = load_distance_matrix(str(matrix_path))

    assert names == ["A", "B", "C"]
    assert matrix == [
        [0.0, 5.0, 9.0],
        [5.0, 0.0, 10.0],
        [9.0, 10.0, 0.0],
    ]


@pytest.mark.unit
def test_build_neighbor_joining_tree(tmp_path: Path) -> None:
    tree = build_neighbor_joining_tree(
        ["A", "B", "C", "D"],
        [
            [0.0, 5.0, 9.0, 9.0],
            [5.0, 0.0, 10.0, 10.0],
            [9.0, 10.0, 0.0, 8.0],
            [9.0, 10.0, 8.0, 0.0],
        ],
    )

    terminal_names = sorted(
        node["name"] for node in get_terminals(tree) if node["name"] is not None
    )
    assert terminal_names == ["A", "B", "C", "D"]
    assert len(get_nonterminals(tree)) == 3


@pytest.mark.unit
def test_to_newick_and_write_newick(tmp_path: Path) -> None:
    tree: TreeNode = {
        "name": None,
        "branch_length": 0.0,
        "children": [
            {"name": "A", "branch_length": 1.0, "children": []},
            {"name": "B value", "branch_length": 2.5, "children": []},
        ],
    }

    output_path = tmp_path / "tree.newick"
    generated_path = write_newick(tree, str(output_path))

    assert generated_path == output_path
    assert output_path.read_text(encoding="utf-8") == "(A:1,'B value':2.5):0;\n"
    assert to_newick(tree) == "(A:1,'B value':2.5):0;\n"


@pytest.mark.unit
def test_run_builds_report_and_file(tmp_path: Path) -> None:
    input_path = tmp_path / "matrix.csv"
    output_path = tmp_path / "tree.newick"
    input_path.write_text(
        ",A,B,C\nA,0,5,9\nB,5,0,10\nC,9,10,0\n",
        encoding="utf-8",
    )

    report = run(str(input_path), str(output_path))

    assert report == {
        "status": "success",
        "distance_matrix_path": str(input_path),
        "tree_format": "newick",
        "total_leaf_nodes": 3,
        "total_internal_nodes": 2,
        "output_file_path": str(output_path),
    }
    assert output_path.read_text(encoding="utf-8").endswith(";\n")
