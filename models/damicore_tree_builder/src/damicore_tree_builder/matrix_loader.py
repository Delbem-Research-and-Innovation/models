"""Load and validate distance matrices from CSV files."""

import csv
import math
from pathlib import Path

DEFAULT_INPUT_PATH = (
    "/models/fixtures/dataset-seade-pop-age/output-distance-ncd-gzip-cod_distr-ano-idade.csv"
)


class MatrixLoader:
    """Loads a square, symmetric distance matrix from a labeled CSV file."""

    def __init__(self, input_path: str = DEFAULT_INPUT_PATH) -> None:
        self.input_path = Path(input_path)

    def load(self) -> tuple[list[str], list[list[float]]]:
        """Return row labels and numeric distances from the configured CSV file."""
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        rows = self._read_rows()
        names, matrix = self._parse_rows(rows)
        self._validate(names, matrix)

        return names, matrix

    def _read_rows(self) -> list[list[str]]:
        try:
            with self.input_path.open(newline="", encoding="utf-8") as csv_file:
                return list(csv.reader(csv_file))
        except csv.Error as exc:
            raise ValueError(f"Could not parse CSV file: {self.input_path}") from exc

    def _parse_rows(self, rows: list[list[str]]) -> tuple[list[str], list[list[float]]]:
        if not rows:
            raise ValueError(f"Input CSV file is empty: {self.input_path}")

        header = rows[0]
        if len(header) < 2:
            raise ValueError("Distance matrix header must contain at least one label.")

        column_labels = header[1:]
        row_labels: list[str] = []
        matrix: list[list[float]] = []

        for row_number, row in enumerate(rows[1:], start=2):
            if len(row) != len(header):
                raise ValueError(
                    "Distance matrix rows must have the same number of columns as the header. "
                    f"Row {row_number} has {len(row)} columns, expected {len(header)}."
                )

            row_labels.append(row[0])
            try:
                matrix.append([float(value) for value in row[1:]])
            except ValueError as exc:
                raise ValueError("Distance matrix contains non-numeric values.") from exc

        if row_labels != column_labels:
            raise ValueError(
                "Row labels and column labels must match and appear in the same order."
            )

        return row_labels, matrix

    def _validate(self, names: list[str], matrix: list[list[float]]) -> None:
        if not names or not matrix:
            raise ValueError("Distance matrix is empty.")

        if len(set(names)) != len(names):
            raise ValueError("Distance matrix contains duplicated labels.")

        rows = len(matrix)
        columns = {len(row) for row in matrix}
        if len(columns) != 1 or rows != len(names) or columns.pop() != len(names):
            raise ValueError("Distance matrix must be square.")

        for row_index, row in enumerate(matrix):
            for column_index, value in enumerate(row):
                if value < 0:
                    raise ValueError("Distance matrix cannot contain negative values.")

                if row_index == column_index and not math.isclose(value, 0.0, abs_tol=1e-9):
                    raise ValueError("Distance matrix diagonal must contain only zeros.")

                transposed_value = matrix[column_index][row_index]
                if not math.isclose(value, transposed_value, rel_tol=1e-9, abs_tol=1e-12):
                    raise ValueError("Distance matrix must be symmetric.")
