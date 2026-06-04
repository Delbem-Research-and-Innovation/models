"""Column Matcher Similarity Analysis Module.

This module provides functional utilities for identifying similar column names
between two data schemas using fuzzy string matching.

Note on implementation:
- All functions are pure and side-effect free.
- Lazy evaluation used for large datasets to optimize memory usage.
- Normalization uses caching to avoid redundant computations.
"""

import re
from collections.abc import Generator
from functools import lru_cache
from itertools import product
from typing import Any

from thefuzz import (  # pyright: ignore[reportMissingTypeStubs]  # thefuzz has no published type stubs
    fuzz,
)


@lru_cache(maxsize=256)
def normalize_camel_case(text: str) -> str:
    """Convert CamelCase to space-separated lowercase words.

    Cached to avoid redundant computation for repeated inputs.

    Parameters
    ----------
    text : str
        Input text potentially in CamelCase format.

    Returns
    -------
    str
        Normalized text with CamelCase converted to space-separated words.

    Examples
    --------
    >>> normalize_camel_case("IdCliente")
    'id cliente'
    >>> normalize_camel_case("normalText")
    'normal text'
    """
    # Insert space before uppercase letters that follow lowercase
    camel_spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    # Insert space before sequences of uppercase followed by lowercase
    camel_spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", camel_spaced)
    return camel_spaced.lower()


@lru_cache(maxsize=256)
def remove_underscores(text: str) -> str:
    """Replace underscores with spaces.

    Cached to avoid redundant computation for repeated inputs.

    Parameters
    ----------
    text : str
        Input text potentially containing underscores.

    Returns
    -------
    str
        Text with underscores replaced by spaces.

    Examples
    --------
    >>> remove_underscores("ID_CLIENTE")
    'ID CLIENTE'
    """
    return text.replace("_", " ")


@lru_cache(maxsize=256)
def normalize_column_name(name: str) -> str:
    """Normalize column name for comparison.

    Applies multiple normalization steps:
    1. Remove underscores (replace with spaces)
    2. Convert CamelCase to space-separated words
    3. Convert to lowercase
    4. Strip extra whitespace

    Cached to avoid redundant computation.

    Parameters
    ----------
    name : str
        Raw column name. Empty strings are returned as-is.

    Returns
    -------
    str
        Normalized column name.

    Raises
    ------
    TypeError
        If name is not a string.

    Examples
    --------
    >>> normalize_column_name("ID_CLIENTE")
    'id cliente'
    >>> normalize_column_name("IdCliente")
    'id cliente'
    >>> normalize_column_name("id_cliente")
    'id cliente'
    >>> normalize_column_name("")
    ''
    """
    if not name:
        return ""
    with_spaces = remove_underscores(name)
    camel_normalized = normalize_camel_case(with_spaces)
    return " ".join(camel_normalized.split())


@lru_cache(maxsize=512)
def similarity_score(source: str, target: str) -> float:
    """Calculate similarity score between two column names.

    Normalizes both names before comparison:
    - Removes underscores
    - Converts CamelCase to space-separated words
    - Performs case-insensitive fuzzy matching

    Cached to avoid redundant computation for repeated pairs.

    Parameters
    ----------
    source : str
        Source column name. Empty strings are allowed.
    target : str
        Target column name. Empty strings are allowed.

    Returns
    -------
    float
        Similarity score between 0.0 and 1.0.
        Returns 1.0 if both names are empty.
        Returns 0.0 if one is empty and the other is not.

    Examples
    --------
    >>> similarity_score("ID_CLIENTE", "id_cliente")
    1.0
    >>> similarity_score("IdCliente", "id_cliente")
    1.0
    >>> similarity_score("", "")
    1.0
    >>> similarity_score("", "name")
    0.0
    """
    normalized_source = normalize_column_name(source)
    normalized_target = normalize_column_name(target)
    score: int = fuzz.ratio(normalized_source, normalized_target)  # type: ignore[reportUnknownMemberType]  # thefuzz is untyped
    return score / 100.0


def validate_threshold(threshold: float) -> float:
    """Validate similarity threshold.

    Parameters
    ----------
    threshold : float
        Threshold value to validate.

    Returns
    -------
    float
        Validated threshold.

    Raises
    ------
    ValueError
        If threshold is not between 0.0 and 1.0.
    """
    if not (0.0 <= threshold <= 1.0):
        raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")
    return threshold


def _generate_scored_pairs(
    source_columns: list[str],
    target_columns: list[str],
) -> Generator[dict[str, Any], None, None]:
    """Generate scored pairs lazily to optimize memory usage.

    Parameters
    ----------
    source_columns : list[str]
        List of source column names.
    target_columns : list[str]
        List of target column names.

    Yields
    ------
    dict[str, Any]
        Match dictionaries with 'source', 'target', and 'score' keys.
    """
    for src, tgt in product(source_columns, target_columns):
        yield {"source": src, "target": tgt, "score": similarity_score(src, tgt)}


def find_column_matches(
    source_columns: list[str],
    target_columns: list[str],
    threshold: float = 0.8,
) -> list[dict[str, Any]]:
    """Find column matches with similarity above threshold.

    Prioritizes exact matches (score=1.0) and returns them immediately.
    For partial matches, returns all above threshold sorted by score descending.
    Uses lazy evaluation to handle large datasets efficiently.

    Parameters
    ----------
    source_columns : list[str]
        List of source column names. Can be empty.
    target_columns : list[str]
        List of target column names. Can be empty.
    threshold : float, optional
        Minimum similarity threshold, by default 0.8.
        Must be between 0.0 and 1.0.

    Returns
    -------
    list[dict[str, Any]]
        List of matches with 'source', 'target', and 'score' keys.
        Returns empty list if no matches found or if either input is empty.
        Sorted by score descending.

    Raises
    ------
    ValueError
        If threshold is not between 0.0 and 1.0.

    Notes
    -----
    When threshold=1.0, only exact matches are returned.
    When threshold=0.0, all pairs are returned sorted by similarity.
    Exact matches (score=1.0) always take priority and are returned first.
    """
    validate_threshold(threshold)

    # Handle empty inputs early
    if not source_columns or not target_columns:
        return []

    # Generate and filter pairs lazily
    filtered_pairs = [
        pair
        for pair in _generate_scored_pairs(source_columns, target_columns)
        if pair["score"] >= threshold
    ]

    # Prioritize exact matches
    exact_matches = [pair for pair in filtered_pairs if pair["score"] == 1.0]
    if exact_matches:
        return exact_matches

    # Sort by score descending for partial matches (stable sort)
    return sorted(filtered_pairs, key=lambda x: x["score"], reverse=True)
