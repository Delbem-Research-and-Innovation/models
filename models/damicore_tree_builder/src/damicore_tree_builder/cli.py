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
