from pathlib import Path

import pytest

from damicore_normalizer import NormalizerInput, normalize_dataset


@pytest.mark.unit
def test_smoke_runs_on_fixture(contract: NormalizerInput) -> None:
    result = normalize_dataset(contract)
    assert result["status"] == "success"
    assert result["total_files_generated"] == 16896


@pytest.mark.unit
def test_filename_format(contract: NormalizerInput) -> None:
    result = normalize_dataset(contract)
    output_dir = Path(result["output_directory_path"])
    assert (output_dir / "80001_2000_00a04.txt").exists()


@pytest.mark.unit
def test_file_content_only_content_columns(contract: NormalizerInput) -> None:
    result = normalize_dataset(contract)
    output_dir = Path(result["output_directory_path"])
    sample_file = output_dir / "80001_2000_00a04.txt"
    lines = sample_file.read_text(encoding="latin-1").strip().split("\n")
    assert len(lines) == 2
    for line in lines:
        parts = line.split(";")
        assert len(parts) == 2


@pytest.mark.unit
def test_invalid_split_strategy_type_raises(contract: NormalizerInput) -> None:
    contract["split_strategy"]["type"] = "sliding_window"
    with pytest.raises(ValueError, match="composite_keys"):
        normalize_dataset(contract)


@pytest.mark.unit
def test_sample_files_names_has_three(contract: NormalizerInput) -> None:
    result = normalize_dataset(contract)
    assert len(result["sample_files_names"]) == 3


@pytest.mark.unit
def test_output_file_has_no_header(contract: NormalizerInput) -> None:
    result = normalize_dataset(contract)
    output_dir = Path(result["output_directory_path"])
    sample_file = output_dir / "80001_2000_00a04.txt"

    content = sample_file.read_text(encoding="latin-1")

    assert "sexo" not in content
    assert "populacao" not in content


@pytest.mark.unit
def test_naming_convention(contract: NormalizerInput) -> None:
    result = normalize_dataset(contract)

    assert result["naming_convention"] == "{cod_distr}_{ano}_{Idade}.txt"
