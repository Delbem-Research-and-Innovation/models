from pathlib import Path

import pytest

from damicore_normalizer import NormalizerInput

FIXTURES_DIR = (
    Path(__file__).resolve().parents[2] / "fixtures" / "dataset-seade-pop-age"
)


@pytest.fixture
def contract() -> NormalizerInput:
    return {
        "source_file_path": str(FIXTURES_DIR / "raw-dataset-seade-pop-age.csv"),
        "split_strategy": {
            "type": "composite_keys",
            "key_columns": ["cod_distr", "ano", "Idade"],
            "content_columns": ["sexo", "populacao"],
        },
        "output_folder_name": "output-normalizer-cod_distr-ano-idade",
    }
