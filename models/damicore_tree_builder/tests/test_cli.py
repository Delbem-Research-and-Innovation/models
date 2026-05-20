from pathlib import Path

import pytest

from damicore_tree_builder.cli import run


@pytest.mark.unit
def test_run_builds_newick_and_report(tmp_path: Path) -> None:
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
