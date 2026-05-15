"""
Command-line interface for the DAMICORE Neighbor-Joining tree builder.

This module provides the CLI entry point responsible for running the full
pipeline:

1. Load a distance matrix from a CSV file.
2. Build a Neighbor-Joining tree.
3. Save the tree in Newick format.
4. Print a JSON execution report.
"""

# Libraries
import argparse
import json
from pathlib import Path
from typing import Any, Dict

from damicore_tree_builder.matrix_loader import MatrixLoader
from damicore_tree_builder.neighbor_joining import NeighborJoining
from damicore_tree_builder.newick_writer import NewickWriter


def parse_args() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Build a Neighbor-Joining tree from a distance matrix CSV."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input distance matrix CSV file.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where the output Newick tree file will be saved.",
    )

    return parser.parse_args()

