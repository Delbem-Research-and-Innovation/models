import pytest

from column_matcher.matcher import (
    find_column_matches,
    normalize_camel_case,
    normalize_column_name,
    remove_underscores,
    similarity_score,
)

# ======================== Normalization Tests ========================


@pytest.mark.unit
def test_normalize_camel_case() -> None:
    """Test CamelCase normalization."""
    assert normalize_camel_case("IdCliente") == "id cliente"
    assert normalize_camel_case("normalText") == "normal text"
    assert normalize_camel_case("HTTPResponse") == "http response"
    assert normalize_camel_case("id") == "id"


@pytest.mark.unit
def test_remove_underscores() -> None:
    """Test underscore removal."""
    assert remove_underscores("ID_CLIENTE") == "ID CLIENTE"
    assert remove_underscores("id_cliente") == "id cliente"
    assert remove_underscores("no_underscores_here") == "no underscores here"


@pytest.mark.unit
def test_normalize_column_name() -> None:
    """Test full column name normalization."""
    assert normalize_column_name("ID_CLIENTE") == "id cliente"
    assert normalize_column_name("IdCliente") == "id cliente"
    assert normalize_column_name("id_cliente") == "id cliente"
    assert normalize_column_name("ID_Client") == "id client"


@pytest.mark.unit
def test_normalize_column_name_empty_string() -> None:
    """Test normalization of empty strings."""
    assert normalize_column_name("") == ""


@pytest.mark.unit
def test_normalize_column_name_with_numbers() -> None:
    """Test normalization with numbers in names."""
    assert normalize_column_name("id2") == "id2"
    assert normalize_column_name("ID_2") == "id 2"
    assert normalize_column_name("col_name_123") == "col name 123"


@pytest.mark.unit
def test_normalize_column_name_with_spaces() -> None:
    """Test normalization with existing spaces."""
    assert normalize_column_name("user name") == "user name"
    assert normalize_column_name("first  middle  last") == "first middle last"


# ======================== Similarity Score Tests ========================


@pytest.mark.unit
def test_similarity_score_empty_strings() -> None:
    """Test similarity between empty strings."""
    assert similarity_score("", "") == 1.0


@pytest.mark.unit
def test_similarity_score_one_empty() -> None:
    """Test similarity when one string is empty."""
    assert similarity_score("", "name") == 0.0
    assert similarity_score("name", "") == 0.0


@pytest.mark.unit
def test_similarity_score_identical() -> None:
    """Test similarity of identical strings."""
    assert similarity_score("name", "name") == 1.0
    assert similarity_score("user_id", "user_id") == 1.0


@pytest.mark.unit
def test_similarity_score_case_insensitive() -> None:
    """Test case-insensitive similarity."""
    assert similarity_score("Name", "name") == 1.0
    assert similarity_score("USER_ID", "user_id") == 1.0


@pytest.mark.unit
def test_similarity_score_camel_vs_snake() -> None:
    """Test similarity between CamelCase and snake_case."""
    assert similarity_score("IdCliente", "id_cliente") == 1.0
    assert similarity_score("ClienteId", "cliente_id") == 1.0


@pytest.mark.unit
def test_similarity_score_with_numbers() -> None:
    """Test similarity with numbers."""
    assert similarity_score("id2", "id_2") > 0.8
    assert similarity_score("col_name_123", "colName123") > 0.8


# ======================== Exact Match Tests ========================


@pytest.mark.unit
def test_exact_match() -> None:
    """Test exact matches with 100% similarity."""
    source_columns = ["name", "age"]
    target_columns = ["name", "age", "city"]
    result = find_column_matches(source_columns, target_columns, threshold=0.8)

    # Should return exact matches with score 1.0
    expected = [
        {"source": "name", "target": "name", "score": 1.0},
        {"source": "age", "target": "age", "score": 1.0},
    ]
    assert result == expected


@pytest.mark.unit
def test_exact_match_with_normalization() -> None:
    """Test exact matches after normalization."""
    source_columns = ["ID_CLIENTE"]
    target_columns = ["id_cliente"]
    result = find_column_matches(source_columns, target_columns, threshold=0.8)

    assert len(result) == 1
    assert result[0]["source"] == "ID_CLIENTE"
    assert result[0]["target"] == "id_cliente"
    assert result[0]["score"] == 1.0


# ======================== Partial Match Tests ========================


@pytest.mark.unit
def test_partial_match() -> None:
    """Test partial matches with case-insensitive similarity."""
    source_columns = ["ID_CLIENTE", "Nome"]
    target_columns = ["id_cliente", "nome", "endereco"]
    result = find_column_matches(source_columns, target_columns, threshold=0.8)

    # Should return exact matches first
    assert len(result) == 2
    for match in result:
        assert match["score"] == 1.0
        assert match["source"] in source_columns
        assert match["target"] in target_columns


@pytest.mark.unit
def test_partial_match_with_plurals() -> None:
    """Test matches with plural forms."""
    source_columns = ["cliente"]
    target_columns = ["clientes"]
    result = find_column_matches(source_columns, target_columns, threshold=0.8)

    # Plurals have high but not perfect similarity
    assert len(result) >= 1
    assert result[0]["source"] == "cliente"
    assert result[0]["target"] == "clientes"
    assert 0.8 <= result[0]["score"] <= 1.0


@pytest.mark.unit
def test_partial_match_with_prefixes() -> None:
    """Test matches with different prefixes."""
    source_columns = ["id_cliente"]
    target_columns = ["id_cliente_origem"]
    result = find_column_matches(source_columns, target_columns, threshold=0.7)

    # Partial match should be found with lower threshold
    assert len(result) >= 1
    assert result[0]["score"] >= 0.7


# ======================== Threshold Tests ========================


@pytest.mark.unit
def test_below_threshold_ignored() -> None:
    """Test that matches below threshold are ignored."""
    source_columns = ["abc", "def"]
    target_columns = ["xyz", "uvw"]
    result = find_column_matches(source_columns, target_columns, threshold=0.8)

    # All matches should meet threshold or result is empty
    assert all(match["score"] >= 0.8 for match in result)


@pytest.mark.unit
def test_threshold_zero_returns_all() -> None:
    """Test that threshold=0.0 returns all pairs."""
    source_columns = ["abc"]
    target_columns = ["xyz"]
    result = find_column_matches(source_columns, target_columns, threshold=0.0)

    # Should return the pair even with low similarity
    assert len(result) == 1
    assert result[0]["source"] == "abc"
    assert result[0]["target"] == "xyz"
    assert result[0]["score"] >= 0.0


@pytest.mark.unit
def test_threshold_one_returns_only_exact() -> None:
    """Test that threshold=1.0 returns only exact matches."""
    source_columns = ["name", "abc"]
    target_columns = ["name", "xyz"]
    result = find_column_matches(source_columns, target_columns, threshold=1.0)

    # Should return only the exact match
    assert len(result) == 1
    assert result[0]["source"] == "name"
    assert result[0]["target"] == "name"
    assert result[0]["score"] == 1.0


@pytest.mark.unit
def test_invalid_threshold_value_error() -> None:
    """Test ValueError for invalid thresholds outside 0-1."""
    source_columns = ["name"]
    target_columns = ["name"]

    with pytest.raises(ValueError):
        find_column_matches(source_columns, target_columns, threshold=-0.1)

    with pytest.raises(ValueError):
        find_column_matches(source_columns, target_columns, threshold=1.1)


# ======================== Edge Case Tests ========================


@pytest.mark.unit
def test_empty_source_columns() -> None:
    """Test with empty source columns list."""
    result = find_column_matches([], ["name", "age"], threshold=0.8)
    assert result == []


@pytest.mark.unit
def test_empty_target_columns() -> None:
    """Test with empty target columns list."""
    result = find_column_matches(["name"], [], threshold=0.8)
    assert result == []


@pytest.mark.unit
def test_both_empty_columns() -> None:
    """Test with both empty column lists."""
    result = find_column_matches([], [], threshold=0.8)
    assert result == []


@pytest.mark.unit
def test_single_columns() -> None:
    """Test with single column in each list."""
    result = find_column_matches(["name"], ["name"], threshold=0.8)
    assert len(result) == 1
    assert result[0]["score"] == 1.0


@pytest.mark.unit
def test_many_columns() -> None:
    """Test with large number of columns."""
    source = [f"col_{i}" for i in range(50)]
    target = [f"col_{i}" for i in range(50)]
    result = find_column_matches(source, target, threshold=0.8)

    # Should find 50 exact matches
    assert len(result) == 50
    assert all(m["score"] == 1.0 for m in result)


@pytest.mark.unit
def test_multiple_same_score_ordering() -> None:
    """Test ordering of results with multiple matches at same score."""
    source_columns = ["id"]
    target_columns = ["id", "idx", "i_d"]
    result = find_column_matches(source_columns, target_columns, threshold=0.0)

    # Should be sorted by score descending
    assert result[0]["score"] >= result[-1]["score"] if result else True
    # Exact match should be first (when threshold allows multiple)
    assert any(m["score"] == 1.0 for m in result)


@pytest.mark.unit
def test_special_characters_normalization() -> None:
    """Test handling of special characters."""
    # Note: current implementation doesn't handle special chars,
    # but we test to document behavior
    source_columns = ["col-name"]
    target_columns = ["col-name"]
    result = find_column_matches(source_columns, target_columns, threshold=0.8)

    # Should find match (hyphens preserved)
    assert len(result) >= 1
