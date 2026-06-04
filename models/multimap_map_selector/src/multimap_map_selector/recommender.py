"""Core recommendation logic for multimap_map_selector.

Composes profiling, rule matching, and choropleth generation into a single
callable that takes a CSV path and returns a `RecommendationResult`.
"""

from __future__ import annotations

from pathlib import Path

from .choropleth import generate_choropleth_json
from .profiling import profile_dataset
from .rules import select_map_type
from .types import RecommendationResult, RecommenderStrategy


def recommend_visualization_spec(
    source_file_path: str | Path,
    strategy: RecommenderStrategy,
    output_directory: str | Path | None = None,
) -> RecommendationResult:
    """Recommend and serialise a visualization spec for a CSV dataset.

    Parameters
    ----------
    source_file_path : str | Path
        Path to the CSV dataset to profile and evaluate.
    strategy : RecommenderStrategy
        User-specified preferences (target library, fallback map).
    output_directory : str | Path | None, optional
        Directory where the chosen visualization spec will be written as JSON.
        Defaults to the current working directory.

    Returns
    -------
    RecommendationResult
        Serializable object describing success/failure, paths, and the spec.

    Raises
    ------
    FileNotFoundError
        If ``source_file_path`` does not exist.
    """
    source_path = Path(source_file_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    profile = profile_dataset(source_path)
    candidate = select_map_type(profile, strategy)
    if candidate is None:
        reason = (
            "No spatial columns found in the dataset. "
            "Choropleth visualization requires geographic identifiers."
            if not profile.spatial_columns
            else "No map type matches the dataset structure."
        )
        return RecommendationResult(
            status="failure",
            source_file=str(source_path),
            visualization_spec={"reason": reason},
            output_spec_path="",
        )

    if candidate.layer_type != "choropleth":
        return RecommendationResult(
            status="failure",
            source_file=str(source_path),
            visualization_spec={
                "reason": f"Map type '{candidate.layer_type}' is not yet serializable."
            },
            output_spec_path="",
        )

    out_dir = Path(output_directory) if output_directory is not None else None
    output_path = generate_choropleth_json(source_path, profile, candidate, out_dir)
    return RecommendationResult(
        status="success",
        source_file=str(source_path),
        visualization_spec=candidate.to_dict(),
        output_spec_path=str(output_path),
    )
