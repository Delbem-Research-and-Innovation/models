"""Type definitions for the multimap_map_selector package.

This module defines small, immutable dataclasses used across the package:
- `RecommenderStrategy`: user-provided strategy/constraints for the recommender.
- `VisualizationSpec`: a concrete visualization specification candidate.
- `RecommendationResult`: the public return object of the API.
- `DatasetProfile`: metadata summary produced by dataset profiling.

Keep these types lightweight and serializable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RecommenderStrategy:
    """User-supplied strategy controls for the recommender.

    Attributes
    ----------
    target_library: str
        The visualization library target (e.g., "geovis").
    fallback_map: str
        A fallback map identifier used when no perfect match is found.
    """

    target_library: str
    fallback_map: str


@dataclass(frozen=True)
class VisualizationSpec:
    """A candidate visualization specification.

    This holds the minimal fields needed by downstream renderers and by tests.
    Use `to_dict()` to produce a JSON-friendly representation.
    """

    id: str
    engine: str
    layer_type: str
    data_points_mapped: int
    join_key: str | None = None
    value_column: str | None = None
    normalize_by: str | None = None
    rationale: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary representation.

        Avoid including non-serializable objects here.
        """
        return {
            "id": self.id,
            "engine": self.engine,
            "layer_type": self.layer_type,
            "data_points_mapped": self.data_points_mapped,
            "join_key": self.join_key,
            "value_column": self.value_column,
            "normalize_by": self.normalize_by,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class RecommendationResult:
    """Public return type from `recommend_visualization_spec`.

    Fields are deliberately simple so the object can be easily serialized
    and asserted in tests.
    """

    status: str
    source_file: str
    visualization_spec: dict[str, Any]
    output_spec_path: str


@dataclass(frozen=True)
class DatasetProfile:
    """Summary metadata produced when profiling a dataset.

    Attributes
    ----------
    source_file: Path
        Path to the source dataset.
    columns: list[str]
        Column names found in the header.
    spatial_columns: list[str]
        Columns recognised as spatial identifiers.
    numeric_columns: list[str]
        Columns recognised as numeric / quantitative measures.
    categorical_columns: list[str]
        Remaining columns considered categorical.
    row_count: int
        Number of data rows in the file.
    delimiter: str
        Detected CSV delimiter.
    age_column : str | None
        Column name holding age group values (e.g. ``'Idade'``), if detected.
    year_column : str | None
        Column name holding year values (e.g. ``'ano'``), if detected.
    """

    source_file: Path
    columns: list[str]
    spatial_columns: list[str]
    numeric_columns: list[str]
    categorical_columns: list[str]
    row_count: int
    delimiter: str
    has_age_60_64: bool = False
    has_point_coords: bool = False
    age_column: str | None = None
    year_column: str | None = None
