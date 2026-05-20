"""Command-line interface for the DAMICORE Neighbor-Joining tree builder."""

import argparse
import json
from pathlib import Path
from typing import Any

from damicore_tree_builder.matrix_loader import MatrixLoader
from damicore_tree_builder.neighbor_joining import NeighborJoining
from damicore_tree_builder.newick_writer import NewickWriter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Neighbor-Joining tree from a distance matrix CSV."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input distance matrix CSV file.",
    )
    parser.add_argument(
        "--output", required=True, help="Path where the output Newick tree file will be saved."
    )

    return parser.parse_args()


def build_success_report(
    input_path: Path,
    output_path: Path,
    total_leaf_nodes: int,
    total_internal_nodes: int,
) -> dict[str, Any]:
    return {
        "status": "success",
        "distance_matrix_path": str(input_path),
        "tree_format": "newick",
        "total_leaf_nodes": total_leaf_nodes,
        "total_internal_nodes": total_internal_nodes,
        "output_file_path": str(output_path),
    }


def build_error_report(error: Exception) -> dict[str, str]:
    return {
        "status": "error",
        "message": str(error),
    }


def run(input_path: str, output_path: str) -> dict[str, Any]:
    input_file_path = Path(input_path)
    output_file_path = Path(output_path)

    names, matrix = MatrixLoader(str(input_file_path)).load()
    tree = NeighborJoining(names, matrix).build_tree()
    generated_path = NewickWriter(str(output_file_path)).write(tree)

    return build_success_report(
        input_path=input_file_path,
        output_path=generated_path,
        total_leaf_nodes=len(tree.get_terminals()),
        total_internal_nodes=len(tree.get_nonterminals()),
    )


def main() -> None:
    args = parse_args()

    try:
        report = run(args.input, args.output)
    except (FileNotFoundError, ValueError) as error:
        report = build_error_report(error)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
