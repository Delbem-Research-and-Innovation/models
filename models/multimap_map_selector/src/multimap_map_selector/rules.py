"""Rule-based matcher that converts a DatasetProfile into a VisualizationSpec.

This module implements simple, deterministic rules inspired by the Desk
Research PDF. Rules are intentionally readable so they can be extended with
additional heuristics (normalisation checks, uncertainty, MAUP warnings, etc.).
"""

from __future__ import annotations

from .types import DatasetProfile, RecommenderStrategy, VisualizationSpec


def select_map_type(
    profile: DatasetProfile, strategy: RecommenderStrategy
) -> VisualizationSpec | None:
    """Select a map type for the given profile.

    Priority order:

    1. Heatmap: point coordinates (lat/lon) with a numeric value.
    2. Small multiples: two or more numeric variables alongside a spatial key.
    3. Choropleth: spatial key + numeric variable with a normalization signal
       (rate/percentage column, age-group data, or single numeric column).
    4. Proportional symbol: spatial key + numeric variable, no normalization
       signal — raw counts by zone.
    """
    # 1. Heatmap (point coordinates)
    heat = _match_heatmap(profile)
    if heat:
        return heat

    # 2. Small multiples (multiple quantitative variables)
    small = _match_small_multiples(profile)
    if small:
        return small

    if not profile.spatial_columns or not profile.numeric_columns:
        return None

    # 3. Choropleth — requires a normalization signal to avoid misleading maps.
    def _is_rate_like(name: str) -> bool:
        n = name.lower()
        return any(tok in n for tok in ("taxa", "perc", "percent", "rate"))

    choropleth_warranted = (
        profile.has_age_60_64
        or any(_is_rate_like(n) for n in profile.numeric_columns)
        or len(profile.numeric_columns) == 1
    )
    if choropleth_warranted:
        chor = _match_choropleth(profile)
        if chor:
            return chor

    # 4. Proportional symbol fallback
    return _match_proportional_symbol(profile)


def _match_choropleth(profile: DatasetProfile) -> VisualizationSpec | None:
    """Match choropleth when there is an area identifier and a quantitative field.

    The Desk Research recommends normalising values (e.g., rates) before
    mapping. Normalisation is not performed here, but the presence of a
    numeric column signals choropleth is a valid candidate.
    """
    if not profile.spatial_columns or not profile.numeric_columns:
        return None

    join_key = profile.spatial_columns[0]

    # Prefer an explicit rate-like column if present
    def _is_rate_like(name: str) -> bool:
        n = name.lower()
        tokens = ("taxa", "perc", "percent", "rate", "per_1000", "per_10000", "per_mil")
        return any(tok in n for tok in tokens)

    rate_cols = [c for c in profile.numeric_columns if _is_rate_like(c)]
    if rate_cols:
        value_column = rate_cols[0]
        return VisualizationSpec(
            id=f"{join_key}_{value_column}_choropleth",
            engine="maplibre",
            layer_type="choropleth",
            data_points_mapped=profile.row_count,
            join_key=join_key,
            value_column=value_column,
            normalize_by=None,
            rationale="Choropleth on an already-normalised rate/percentage column.",
        )

    # If there is a population-like column we can normalise counts
    def _is_pop_like(name: str) -> bool:
        n = name.lower()
        return any(tok in n for tok in ("pop", "population", "populacao", "pop_total", "total_pop"))

    pop_cols = [c for c in profile.columns if _is_pop_like(c)]
    # Choose the first numeric column that is not the population column
    candidate_values = [c for c in profile.numeric_columns if c not in pop_cols]
    if candidate_values and pop_cols:
        value_column = candidate_values[0]
        pop_column = pop_cols[0]
        return VisualizationSpec(
            id=f"{join_key}_{value_column}_choropleth",
            engine="maplibre",
            layer_type="choropleth",
            data_points_mapped=profile.row_count,
            join_key=join_key,
            value_column=value_column,
            normalize_by=pop_column,
            rationale="Counts will be normalised by population (per 1000) before mapping.",
        )

    # If there's exactly one numeric column and spatial key, allow choropleth
    if len(profile.numeric_columns) == 1:
        value_column = profile.numeric_columns[0]
        return VisualizationSpec(
            id=f"{join_key}_{value_column}_choropleth",
            engine="maplibre",
            layer_type="choropleth",
            data_points_mapped=profile.row_count,
            join_key=join_key,
            value_column=value_column,
            normalize_by=None,
            rationale=(
                "Single quantitative variable across spatial areas; user should ensure"
                " normalization is appropriate (warning included)."
            ),
        )

    return None


def _match_proportional_symbol(profile: DatasetProfile) -> VisualizationSpec | None:
    """Match proportional symbols for counts/volumes by zone.

    Prefer proportional symbols when the user wants to show raw counts rather
    than normalized rates. The rule here is identical to choropleth but the
    chosen layer_type differs; later we can promote this based on metadata or
    `RecommenderStrategy` hints.
    """
    if not profile.spatial_columns or not profile.numeric_columns:
        return None

    join_key = profile.spatial_columns[0]
    value_column = profile.numeric_columns[0]
    return VisualizationSpec(
        id=f"{join_key}_{value_column}_proportional_symbol",
        engine="maplibre",
        layer_type="proportional_symbol",
        data_points_mapped=profile.row_count,
        join_key=join_key,
        value_column=value_column,
        rationale=(
            "Counts or volumes in geographic zones can also be "
            "represented with proportional symbols."
        ),
    )


def _match_heatmap(profile: DatasetProfile) -> VisualizationSpec | None:
    """Match heatmap when point coordinates are present.

    Heatmaps require x/y or lat/lon coordinates. This rule searches for column
    names that look like coordinates and treats the dataset as point-based.
    """
    spatial_columns = [column for column in profile.columns if _is_point_coordinate(column)]
    if not spatial_columns or not profile.numeric_columns:
        return None

    value_column = profile.numeric_columns[0]
    return VisualizationSpec(
        id=f"heatmap_{value_column}",
        engine="maplibre",
        layer_type="heatmap",
        data_points_mapped=profile.row_count,
        join_key=spatial_columns[0],
        value_column=value_column,
        rationale="Point-based continuous values are suitable for heatmap visualization.",
    )


def _match_small_multiples(profile: DatasetProfile) -> VisualizationSpec | None:
    """Match small multiples when multiple quantitative columns exist.

    Small multiples are recommended in the Desk Research when several variables
    need spatial comparison. This rule fires if two or more numeric columns are
    present alongside a spatial key.
    """
    if len(profile.numeric_columns) < 2 or not profile.spatial_columns:
        return None

    return VisualizationSpec(
        id="small_multiples_by_variable",
        engine="maplibre",
        layer_type="small_multiples",
        data_points_mapped=profile.row_count,
        join_key=profile.spatial_columns[0],
        value_column=profile.numeric_columns[0],
        rationale=(
            "Multiple quantitative variables with geographic units benefit from small multiples."
        ),
    )


def _is_point_coordinate(column_name: str) -> bool:
    """Return True if the column name suggests latitude/longitude coordinates."""
    normalized = column_name.strip().lower()
    return any(token in normalized for token in ("lat", "lon", "latitude", "longitude"))
