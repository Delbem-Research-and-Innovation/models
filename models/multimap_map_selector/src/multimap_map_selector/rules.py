"""Rule-based matcher that converts a DatasetProfile into a VisualizationSpec.

This module implements simple, deterministic rules inspired by the Desk
Research PDF. Rules are intentionally readable so they can be extended with
additional heuristics (normalisation checks, uncertainty, MAUP warnings, etc.).
"""

from __future__ import annotations

from .types import DatasetProfile, RecommenderStrategy, VisualizationSpec


def select_map_type(profile: DatasetProfile, strategy: RecommenderStrategy) -> VisualizationSpec | None:
    """Select a map type for the given profile.

    Behaviour with prioritized rules:

    1. Heatmap: if the dataset contains point coordinates (lat/lon) plus a
       numeric value, prefer a heatmap candidate.
    2. Small multiples: if there are two or more numeric variables alongside a
       spatial key, recommend small multiples.
    3. Choropleth (strict): only when a spatial key and numeric variable exist
       AND the dataset matches stricter criteria (e.g. contains age group
       "60 a 64" or a rate/percentage column). This prevents over-generation
       of choropleth specs for datasets that are not conceptually area-based.
    4. Proportional symbol: fallback when spatial key + numeric are present but
       the choropleth strict conditions do not hold.

    The caller (`recommend_visualization_spec`) only serializes choropleth
    outputs; other candidates are returned so the CLI can inform the user.
    """
    # 1. Heatmap (point coordinates)
    heat = _match_heatmap(profile)
    if heat:
        return heat

    # 2. Choropleth (strict): prefer normalized/rate columns even if multiple
    # numeric columns exist — these are commonly mapped as choropleths.
    chor = _match_choropleth(profile)
    if chor:
        return chor

    # 3. Small multiples
    small = _match_small_multiples(profile)
    if small:
        return small

    # 4. Area-based fallbacks
    if not profile.spatial_columns or not profile.numeric_columns:
        return None

    # Strict choropleth conditions: presence of age group 60 a 64 OR a rate-like
    # numeric column (contains taxa/perc/rate/percent).
    def _is_rate_like(name: str) -> bool:
        n = name.lower()
        return any(tok in n for tok in ("taxa", "perc", "percent", "rate"))

    if profile.has_age_60_64 or any(_is_rate_like(n) for n in profile.numeric_columns):
        return _match_choropleth(profile)

    # Fallback: proportional symbol (do not serialize to JSON by default)
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
        return any(tok in n for tok in ("taxa", "perc", "percent", "rate", "per_1000", "per_10000", "per_mil"))

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
        rationale="Counts or volumes in geographic zones can also be represented with proportional symbols.",
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
        rationale="Multiple quantitative variables with geographic units benefit from small multiples.",
    )


def _is_point_coordinate(column_name: str) -> bool:
    """Return True if the column name suggests latitude/longitude coordinates."""
    normalized = column_name.strip().lower()
    return any(token in normalized for token in ("lat", "lon", "latitude", "longitude"))
