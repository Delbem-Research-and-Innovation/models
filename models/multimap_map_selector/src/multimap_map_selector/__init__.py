"""Public API for the multimap_map_selector package.

Expose a single convenience function `recommend_visualization_spec` together
with the small type objects used to configure and receive the result.
"""

from __future__ import annotations

from .recommender import recommend_visualization_spec
from .types import RecommendationResult, RecommenderStrategy, VisualizationSpec

__all__ = [
    "RecommenderStrategy",
    "RecommendationResult",
    "VisualizationSpec",
    "recommend_visualization_spec",
]
