"""Dataset profiling utilities.

These helpers perform lightweight, dependency-free profiling of CSV files to
identify candidate spatial and numeric columns. The heuristic rules are
intentionally simple and can be expanded later.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .types import DatasetProfile


# Common tokens used to recognise spatial identifier columns.
SPATIAL_KEYWORDS = (
    "cod_distr",
    "cod_distrito",
    "cd_distrito",
    "district",
    "distrito",
    "subpref",
    "geocode",
    "geo",
)

# Tokens used to recognise numeric/value columns. This is deliberately broad
# to catch Portuguese/English variants present in fixtures.
NUMERIC_KEYWORDS = (
    "pop",
    "population",
    "count",
    "total",
    "rate",
    "percent",
    "taxa",
    "valor",
)


def detect_delimiter(first_line: str) -> str:
    """Detect the most likely delimiter from the header line.

    Uses Python's built-in csv.Sniffer for robust detection, falling
    back to a simple heuristic count if sniffing fails.
    """
    try:
        # Sniffer is great at figuring out standard CSV dialects dynamically
        dialect = csv.Sniffer().sniff(first_line, delimiters=";, \t")
        return dialect.delimiter
    except csv.Error:
        # Fallback heuristic: prioritises `;` when it appears at least as often as `,`
        if ";" in first_line and first_line.count(";") >= first_line.count(","):
            return ";"
        if "," in first_line:
            return ","
        if "\t" in first_line:
            return "\t"
        return ","


def normalize_column_name(column_name: str) -> str:
    """Normalise a header string for keyword matching."""
    return column_name.strip().lower().replace(" ", "_")


def is_spatial_column_name(column_name: str) -> bool:
    """Return True if the column name looks like a spatial identifier.

    Uses simple substring matches against `SPATIAL_KEYWORDS`.
    """
    normalized = normalize_column_name(column_name)
    return any(keyword in normalized for keyword in SPATIAL_KEYWORDS)


def is_numeric_column_name(column_name: str) -> bool:
    """Return True if the column name looks like a numeric measure."""
    normalized = normalize_column_name(column_name)
    return any(keyword in normalized for keyword in NUMERIC_KEYWORDS)


def profile_dataset(source_file_path: Path) -> DatasetProfile:
    """Produce a `DatasetProfile` summarising the CSV file.

    The function reads the header, detects a delimiter and counts rows. It
    classifies columns into spatial, numeric and categorical using lightweight
    heuristics. The implementation avoids heavy dependencies to keep the
    package minimal; if richer profiling is needed, integrate `pandas` later.
    """
    source_text = source_file_path.read_text(encoding="utf-8", errors="replace")
    first_line = source_text.splitlines()[0] if source_text else ""
    delimiter = detect_delimiter(first_line)

    with source_file_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f"Dataset {source_file_path} is empty") from exc

        columns = [column.strip() for column in header if column.strip()]
        spatial_columns = [column for column in columns if is_spatial_column_name(column)]
        numeric_columns = [column for column in columns if is_numeric_column_name(column)]
        categorical_columns = [
            column for column in columns
            if column not in spatial_columns and column not in numeric_columns
        ]

        # Sample rows to detect specific patterns (e.g. age group '60 a 64') and
        # to identify presence of point coordinates by header names.
        sample_limit = 200
        sampled = 0
        has_age_60_64 = False
        for row in reader:
            if sampled >= sample_limit:
                break
            sampled += 1
            for cell in row:
                if cell and cell.strip().lower() == "60 a 64":
                    has_age_60_64 = True

        # row_count excludes header; reuse file to count all rows precisely
    with source_file_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        # skip header
        try:
            next(reader)
        except StopIteration:
            pass
        row_count = sum(1 for _ in reader)

    # Detect point coordinate columns by name presence
    normalized_cols = [normalize_column_name(c) for c in columns]
    has_point_coords = (
        any("lat" in c for c in normalized_cols) and
        any("lon" in c or "long" in c for c in normalized_cols)
    )

    return DatasetProfile(
        source_file=source_file_path,
        columns=columns,
        spatial_columns=spatial_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        row_count=row_count,
        delimiter=delimiter,
        has_age_60_64=has_age_60_64,
        has_point_coords=has_point_coords,
    )