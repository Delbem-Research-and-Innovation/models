from pathlib import Path

import pytest

from damicore_tree_builder.matrix_loader import MatrixLoader


@pytest.mark.unit
def test_loads_valid_distance_matrix(tmp_path: Path) -> None:
    matrix_path = tmp_path / "matrix.csv"
    matrix_path.write_text(
        ",A,B,C\n"
        "A,0,5,9\n"
        "B,5,0,10\n"
        "C,9,10,0\n",
        encoding="utf-8",
    )

    names, matrix = MatrixLoader(str(matrix_path)).load()

    assert names == ["A", "B", "C"]
    assert matrix == [
        [0.0, 5.0, 9.0],
        [5.0, 0.0, 10.0],
        [9.0, 10.0, 0.0],
    ]


@pytest.mark.unit
def test_rejects_mismatched_labels(tmp_path: Path) -> None:
    matrix_path = tmp_path / "matrix.csv"
    matrix_path.write_text(
        ",A,B,C\n"
        "A,0,5,9\n"
        "B,5,0,10\n"
        "D,9,10,0\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Row labels and column labels"):
        MatrixLoader(str(matrix_path)).load()


@pytest.mark.unit
def test_rejects_non_symmetric_matrix(tmp_path: Path) -> None:
    matrix_path = tmp_path / "matrix.csv"
    matrix_path.write_text(
        ",A,B,C\n"
        "A,0,5,9\n"
        "B,4,0,10\n"
        "C,9,10,0\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="symmetric"):
        MatrixLoader(str(matrix_path)).load()
