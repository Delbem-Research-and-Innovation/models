"""
Neighbor-Joining tree builder module.

This module provides the NeighborJoining class, responsible for building
a phylogenetic tree from a distance matrix using the Neighbor-Joining
algorithm.

The class receives the element names and the full square distance matrix
loaded by MatrixLoader, converts them to the format expected by BioPython,
and then uses BioPython's DistanceTreeConstructor to build the tree.
"""

from typing import List

from Bio.Phylo.BaseTree import Tree
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor

try:
    from damicore_tree_builder.matrix_loader import MatrixLoader
except ModuleNotFoundError:
    from matrix_loader import MatrixLoader


class NeighborJoining:
    """
    Builds a tree using the Neighbor-Joining algorithm.

    The NeighborJoining class receives a list of element names and a full
    square distance matrix. It converts the matrix to BioPython's
    DistanceMatrix format and applies the Neighbor-Joining algorithm.

    BioPython expects the distance matrix in lower triangular format,
    including the diagonal. For example, a full matrix like:

        [
            [0.0, 5.0, 9.0],
            [5.0, 0.0, 10.0],
            [9.0, 10.0, 0.0],
        ]

    must be converted to:

        [
            [0.0],
            [5.0, 0.0],
            [9.0, 10.0, 0.0],
        ]
    """

    def __init__(self, names: List[str], matrix: List[List[float]]) -> None:
        """
        Initializes the NeighborJoining tree builder.

        Args:
            names: List of element names.
            matrix: Full square distance matrix.
        """
        self.names = names
        self.matrix = matrix