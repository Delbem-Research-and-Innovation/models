"""
Distance matrix loader module.

This module provides the MatrixLoader class, responsible for reading a
distance matrix from a CSV file and validating its structure before it is
used by the Neighbor-Joining algorithm.

The expected CSV format contains object names both in the first row and
in the first column. The remaining values represent pairwise distances
between the objects.

Example:

,80001.txt,80002.txt,80003.txt
80001.txt,0.0,0.95,0.88
80002.txt,0.95,0.0,0.94
80003.txt,0.88,0.94,0.0
"""

# Libraries 
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

# Constants
DEFAULT_INPUT_PATH = "/models/fixtures/dataset-seade-pop-age/output-distance-ncd-gzip-cod_distr-ano-idade.csv"

# Class
class MatrixLoader:
    """
    Loads and validates a distance matrix from a CSV file.

    The MatrixLoader class reads a CSV file where rows and columns are labeled
    with the same element names. It extracts the element names, converts the
    distance values to floats, and validates that the matrix is suitable for
    the Neighbor-Joining algorithm.

    The validation checks whether:
    - the matrix is square;
    - row labels and column labels match;
    - the diagonal values are zero or close to zero;
    - the matrix is symmetric;
    - all distance values are numeric;
    - there are no negative distances.

    After validation, the class returns the element names and the distance
    matrix in a format that can be used by the tree-building algorithm.
    """

    # Builder
    def __init__(self, input_path: str = DEFAULT_INPUT_PATH) -> None:
        """
        Initializes the MatrixLoader.

        Args:
            input_path: Path to the CSV file containing the distance matrix.
        """
        self.input_path = Path(input_path)

    # Read CSV 
    def _read_csv(self) -> pd.DataFrame:
        """
        Reads the CSV file as a pandas DataFrame.

        The first column is used as the row index, and the first row is used as
        the column header.

        Returns:
            A pandas DataFrame containing only numeric distance values.
        """
        try:
            dataframe = pd.read_csv(self.input_path, index_col=0)
        except pd.errors.EmptyDataError as exc:
            raise ValueError(f"Input CSV file is empty: {self.input_path}") from exc
        except pd.errors.ParserError as exc:
            raise ValueError(f"Could not parse CSV file: {self.input_path}") from exc

        return dataframe

    # Validation functions
    def _validate_dataframe(self, dataframe: pd.DataFrame) -> None:
        """
        Validates the distance matrix DataFrame.

        Args:
            dataframe: DataFrame read from the CSV file.

        Raises:
            ValueError: If the matrix is not valid.
        """
        if dataframe.empty:
            raise ValueError("Distance matrix is empty.")

        self._validate_square_matrix(dataframe)
        self._validate_labels(dataframe)
        self._validate_numeric_values(dataframe)

        matrix = dataframe.to_numpy(dtype=float)

        self._validate_non_negative_distances(matrix)
        self._validate_zero_diagonal(matrix)
        self._validate_symmetric_matrix(matrix)


    def _validate_square_matrix(self, dataframe: pd.DataFrame) -> None:
        """
        Checks whether the matrix is square.
        """
        rows, columns = dataframe.shape

        if rows != columns:
            raise ValueError(
                f"Distance matrix must be square, but got {rows} rows and {columns} columns."
            )


    def _validate_labels(self, dataframe: pd.DataFrame) -> None:
        """
        Checks whether row labels and column labels match.
        """
        row_labels = list(dataframe.index)
        column_labels = list(dataframe.columns)

        if row_labels != column_labels:
            raise ValueError(
                "Row labels and column labels must match and appear in the same order."
            )

        if len(set(row_labels)) != len(row_labels):
            raise ValueError("Distance matrix contains duplicated row labels.")

        if len(set(column_labels)) != len(column_labels):
            raise ValueError("Distance matrix contains duplicated column labels.")


    def _validate_numeric_values(self, dataframe: pd.DataFrame) -> None:
        """
        Checks whether all values in the matrix are numeric.
        """
        try:
            dataframe.astype(float)
        except ValueError as exc:
            raise ValueError("Distance matrix contains non-numeric values.") from exc


    def _validate_non_negative_distances(self, matrix: np.ndarray) -> None:
        """
        Checks whether all distances are non-negative.
        """
        if np.any(matrix < 0):
            raise ValueError("Distance matrix cannot contain negative values.")


    def _validate_zero_diagonal(self, matrix: np.ndarray) -> None:
        """
        Checks whether the diagonal is zero or close to zero.
        """
        diagonal = np.diag(matrix)

        if not np.allclose(diagonal, 0.0):
            raise ValueError("Distance matrix diagonal must contain only zeros.")


    def _validate_symmetric_matrix(self, matrix: np.ndarray) -> None:
        """
        Checks whether the matrix is symmetric.
        """
        if not np.allclose(matrix, matrix.T):
            raise ValueError("Distance matrix must be symmetric.")
    # ----

    # Main function
    def load(self) -> Tuple[List[str], List[List[float]]]:
        """
        Loads and validates the distance matrix from the CSV file.

        Returns:
            A tuple containing:
            - a list of element names;
            - a square distance matrix as a list of lists of floats.

        Raises:
            FileNotFoundError: If the input file does not exist.
            ValueError: If the CSV content is invalid.
        """
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        dataframe = self._read_csv()
        self._validate_dataframe(dataframe)

        names = list(dataframe.index)
        matrix = dataframe.to_numpy(dtype=float).tolist()

        return names, matrix
    

# Test
if __name__ == "__main__":
    loader = MatrixLoader()

    try:
        names, matrix = loader.load()

        print("Distance matrix loaded successfully.")
        print(f"Input file: {loader.input_path}")
        print(f"Number of elements: {len(names)}")
        print(f"Matrix size: {len(matrix)} x {len(matrix[0]) if matrix else 0}")

        print("\nElement names:")
        for name in names:
            print(f"- {name}")

        print("\nFirst matrix rows:")
        for row in matrix[:5]:
            print(row)

    except (FileNotFoundError, ValueError) as error:
        print(f"Error while loading distance matrix: {error}")