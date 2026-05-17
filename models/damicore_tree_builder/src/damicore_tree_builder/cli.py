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

try:
    from damicore_tree_builder.matrix_loader import MatrixLoader
    from damicore_tree_builder.neighbor_joining import NeighborJoining
    from damicore_tree_builder.newick_writer import NewickWriter
except ModuleNotFoundError:
    from matrix_loader import MatrixLoader
    from neighbor_joining import NeighborJoining
    from newick_writer import NewickWriter


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


def build_success_report(
    input_path: Path,
    output_path: Path,
    total_leaf_nodes: int,
    total_internal_nodes: int,
) -> Dict[str, Any]:
    """
    Builds the success report following the expected output contract.

    Args:
        input_path: Path to the input distance matrix.
        output_path: Path to the generated Newick file.
        total_leaf_nodes: Number of leaf nodes in the generated tree.
        total_internal_nodes: Number of internal nodes in the generated tree.

    Returns:
        A dictionary containing the execution result.
    """
    return {
        "status": "success",
        "distance_matrix_path": str(input_path),
        "tree_format": "newick",
        "total_leaf_nodes": total_leaf_nodes,
        "total_internal_nodes": total_internal_nodes,
        "output_file_path": str(output_path),
    }


def build_error_report(error: Exception) -> Dict[str, Any]:
    """
    Builds an error report in JSON format.

    Args:
        error: Exception raised during execution.

    Returns:
        A dictionary containing the error result.
    """
    return {
        "status": "error",
        "message": str(error),
    }


def run(input_path: str, output_path: str) -> Dict[str, Any]:
    """
    Runs the full Neighbor-Joining pipeline.

    Args:
        input_path: Path to the input distance matrix CSV file.
        output_path: Path where the Newick tree file will be saved.

    Returns:
        A dictionary following the execution contract.
    """
    input_file_path = Path(input_path)
    output_file_path = Path(output_path)

    loader = MatrixLoader(str(input_file_path))
    names, matrix = loader.load()

    builder = NeighborJoining(names, matrix)
    tree = builder.build_tree()

    writer = NewickWriter(str(output_file_path))
    generated_path = writer.write(tree)

    return build_success_report(
        input_path=input_file_path,
        output_path=generated_path,
        total_leaf_nodes=len(tree.get_terminals()),
        total_internal_nodes=len(tree.get_nonterminals()),
    )

if __name__ == "__main__":
    """
    CLI entry point.
    """
    args = parse_args()

    try:
        report = run(args.input, args.output)
    except (FileNotFoundError, ValueError) as error:
        report = build_error_report(error)

    print(json.dumps(report, indent=2))


# RUN: Na raíz do projeto
"""
python models/damicore_tree_builder/src/damicore_tree_builder/cli.py   --input models/fixtures/distance-matrix-output.csv   --output models/fixtures/dataset-seade-pop-age/output-phylo-tree-distance-ncd-gzip-cod_distr-ano-idade.newick
"""