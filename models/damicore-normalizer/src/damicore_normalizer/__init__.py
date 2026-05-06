# dataset: models/fixtures/dataset-seade-pop-age/raw-dataset-seade-pop-age.csv
# output: models/fixtures/dataset-seade-pop-age/


from pathlib import Path
from typing import TypedDict

import pandas as pd


class SplitStrategy(TypedDict):
    type: str
    key_columns: list[str]
    content_columns: list[str]


class NormalizerInput(TypedDict):
    source_file_path: str
    split_strategy: SplitStrategy
    output_folder_name: str


class NormalizerOutput(TypedDict):
    status: str
    source_file: str
    output_directory_path: str
    total_files_generated: int
    naming_convention: str
    sample_files_names: list[str]


def normalize_dataset(contract: NormalizerInput) -> NormalizerOutput:
    df = pd.read_csv(contract["source_file_path"], sep=";", encoding="latin-1")
    output_dir = (
        Path(contract["source_file_path"]).parent / contract["output_folder_name"]
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    print(df)
    raise NotImplementedError("falta implementar o resto")
