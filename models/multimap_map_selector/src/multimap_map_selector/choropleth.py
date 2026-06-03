from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import median
from typing import Any

from .types import DatasetProfile, VisualizationSpec


DEFAULT_CENTER = [-46.6361, -23.5475]


def _percentile(sorted_values: list[int], p: float) -> int:
    if not sorted_values:
        return 0
    k = (len(sorted_values) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[int(k)]
    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return int(round(d0 + d1))


def generate_choropleth_json(
    source_file: Path,
    profile: DatasetProfile,
    spec: VisualizationSpec,
    output_directory: Path | None = None,
) -> Path:
    """Aggregate the CSV and produce a choropleth-style JSON matching the example.

    Behaviour:
    - If `Idade` column exists and contains '60 a 64', filters to latest year and that age.
    - Otherwise aggregates the numeric `value_column` across all rows per join key.
    - Produces JSON with structure similar to `visualization-spec-distrito-populacao-60-64(2).json`.
    """
    if output_directory is None:
        output_directory = Path.cwd()
    output_directory.mkdir(parents=True, exist_ok=True)

    # --- LÓGICA DINÂMICA DE ID ---
    # Usa o .stem do Path para extrair apenas o nome do arquivo (ex: "raw-dataset-seade-pop-age")
    base_name = source_file.stem
    dynamic_spec_id = f"{base_name}--choropleth"
    # -----------------------------

    delimiter = profile.delimiter
    join_key = spec.join_key
    value_column = spec.value_column

    # Read and aggregate (support optional normalization)
    agg: dict[str, int] = {}
    years = set()
    has_age = False
    age_target = "60 a 64"
    with source_file.open("r", encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        
        for row in reader:
            # collect years
            if "ano" in row and row.get("ano"):
                try:
                    years.add(int(row.get("ano")))
                except Exception:
                    pass

            if "Idade" in row and row.get("Idade") == age_target:
                has_age = True

    # Decide filter: if age present, use latest year and that age
    year_to_use = max(years) if years else None

    with source_file.open("r", encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        for row in reader:
            if join_key not in row or value_column not in row:
                continue
            if has_age:
                if row.get("Idade") != age_target:
                    continue
                if year_to_use is not None:
                    try:
                        if int(row.get("ano", "0")) != year_to_use:
                            continue
                    except Exception:
                        pass

            key = row.get(join_key)

            # Compute value (optionally normalise by population/area)
            raw_val = 0.0
            try:
                raw_val = float(row.get(value_column) or 0)
            except Exception:
                try:
                    raw_val = float(row.get(value_column).replace(',', '.'))
                except Exception:
                    raw_val = 0.0

            if spec.normalize_by and spec.normalize_by in row and row.get(spec.normalize_by):
                try:
                    denom = float(row.get(spec.normalize_by) or 0)
                    # per 1000 inhabitants
                    val = (raw_val / denom) * 1000 if denom > 0 else 0
                except Exception:
                    val = raw_val
            else:
                val = raw_val

            # aggregate as integer for JSON simplicity
            try:
                ival = int(round(val))
            except Exception:
                ival = 0
            agg[key] = agg.get(key, 0) + ival

    # Build ordered values and mapData entries
    items = list(agg.items())
    items.sort(key=lambda x: x[0])
    values = [v for _, v in items]
    sorted_values = sorted(values)

    # 4 thresholds for 5 classes (quantiles)
    thresholds = [
        _percentile(sorted_values, 0.2),
        _percentile(sorted_values, 0.4),
        _percentile(sorted_values, 0.6),
        _percentile(sorted_values, 0.8),
    ]

    mapdata_id = f"{dynamic_spec_id}__values"
    mapdata = [
        {"geometryId": str(i + 1), "value": v} for i, (_, v) in enumerate(items)
    ]

    # Compose JSON structure
    payload: dict[str, Any] = {
        "id": dynamic_spec_id,
        "engine": spec.engine,
        "view": {"center": DEFAULT_CENTER, "zoom": 9},
        "sources": [
            {
                "id": f"{dynamic_spec_id}__geo",
                "type": "geojson",
                "data": "https://example.com/geojson_placeholder.geojson",
            }
        ],
        "layers": [
            {
                "id": f"{dynamic_spec_id}__layer",
                "sourceId": f"{dynamic_spec_id}__geo",
                "geometry": "polygon",
                "mapDataId": mapdata_id,
                "activeLegendId": f"{dynamic_spec_id}__legend",
                "paint": {"lineColor": "#000000", "fillOpacity": 1},
            }
        ],
        "mapData": [
            {
                "mapDataId": mapdata_id,
                "mapId": f"{dynamic_spec_id}__geo",
                "joinKey": join_key,
                "data": mapdata,
            }
        ],
        "legends": [
            {
                "id": f"{dynamic_spec_id}__legend",
                "colorBy": {
                    "type": "quantitative",
                    "property": "value",
                    "scale": "threshold",
                    "thresholds": thresholds,
                    "colors": ["#8C8C8C", "#00B89F", "#0093B2", "#0067C5", "#00497A"],
                },
            }
        ],
        "warnings": [
            {
                "type": "aggregation",
                "message": (
                    "This choropleth aggregates data by spatial units. Results "
                    "may change with different spatial units (MAUP). Consider "
                    "normalising by population or area where appropriate."
                ),
            }
        ],
    }

    output_path = output_directory / f"visualization-spec-{dynamic_spec_id}.json"
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    return output_path