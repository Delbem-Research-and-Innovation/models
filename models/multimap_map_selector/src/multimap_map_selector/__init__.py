"""Public API for the multimap_map_selector package.

Expose a single convenience function `recommend_visualization_spec` together
with the small type objects used to configure and receive the result. The
implementation composes profiling, rule matching and serialization helpers.
"""

from __future__ import annotations

from pathlib import Path

from .profiling import profile_dataset
from .rules import select_map_type
from .choropleth import generate_choropleth_json
from .types import RecommenderStrategy, RecommendationResult, VisualizationSpec

__all__ = [
    "RecommenderStrategy",
    "RecommendationResult",
    "VisualizationSpec",
    "recommend_visualization_spec",
]


def recommend_visualization_spec(
    source_file_path: str | Path,
    strategy: RecommenderStrategy,
    output_directory: str | Path | None = None,
) -> RecommendationResult:
    """Top-level convenience function.

    Parameters
    ----------
    source_file_path:
        Path to the CSV dataset to profile and evaluate.
    strategy:
        `RecommenderStrategy` object for user-specified preferences.
    output_directory:
        Optional directory where the chosen visualization spec will be
        written as JSON. If omitted, the current working directory is used.

    Returns
    -------
    RecommendationResult
        A simple serializable object describing success/failure and paths.
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
            visualization_spec={
                "reason": reason,
            },
            output_spec_path="",
        )

    # Only choropleth is supported in this simplified workflow. Generate the
    # full visualization-spec JSON matching the project's example format.
    if candidate.layer_type != "choropleth":
        return RecommendationResult(
            status="failure",
            source_file=str(source_path),
            visualization_spec={"reason": "Only choropleth is supported."},
            output_spec_path="",
        )

    output_path = generate_choropleth_json(
        source_path,
        profile,
        candidate,
        Path(output_directory) if output_directory is not None else None,
    )
    return RecommendationResult(
        status="success",
        source_file=str(source_path),
        visualization_spec=candidate.to_dict(),
        output_spec_path=str(output_path),
    )
