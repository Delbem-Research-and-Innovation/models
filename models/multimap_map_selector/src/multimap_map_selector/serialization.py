"""Utilities for serializing a `VisualizationSpec` to disk.

The serialization is intentionally simple: write a JSON file with UTF-8
encoding and indentation for human readability.
"""

from __future__ import annotations

import json
from pathlib import Path

from .types import VisualizationSpec


def serialize_visualization_spec(
    spec: VisualizationSpec,
    output_directory: Path | None = None,
) -> Path:
    """Write `spec` to `output_directory/<spec.id>.json` and return the Path.

    If `output_directory` is None the current working directory is used. The
    function ensures the output directory exists and writes UTF-8 JSON with
    indentation to improve inspectability.
    """
    if output_directory is None:
        output_directory = Path.cwd()
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / f"{spec.id}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(spec.to_dict(), handle, ensure_ascii=False, indent=2)
    return output_path
