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


def _sanitize_filename_part(value: object) -> str:
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).replace(" ", "")


def normalize_dataset(contract: NormalizerInput) -> NormalizerOutput:
    split_strategy = contract["split_strategy"]
    if split_strategy["type"] != "composite_keys":
        raise ValueError(
            f"split_strategy.type not supported: {split_strategy['type']!r}. "
            "Only 'composite_keys' is implemented."
        )

    key_columns = split_strategy["key_columns"]
    content_columns = split_strategy["content_columns"]

    source_path = Path(contract["source_file_path"]).resolve()
    output_dir = source_path.parent / contract["output_folder_name"]
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source_path, sep=";", encoding="latin-1")

    sample_files_names: list[str] = []
    total_files_generated = 0

    for key_values, group_df in df.groupby(key_columns):
        if isinstance(key_values, tuple):
            parts = [_sanitize_filename_part(v) for v in key_values]
        else:
            parts = [_sanitize_filename_part(key_values)]
        filename = "_".join(parts) + ".txt"
        file_path = output_dir / filename

        content = group_df[content_columns].to_csv(
            sep=";",
            index=False,
            header=False,
            lineterminator="\n",
            float_format="%g",
        )
        file_path.write_text(content, encoding="latin-1")

        total_files_generated += 1
        if len(sample_files_names) < 3:
            sample_files_names.append(filename)

    naming_convention = "_".join(f"{{{col}}}" for col in key_columns) + ".txt"

    return {
        "status": "success",
        "source_file": str(source_path),
        "output_directory_path": str(output_dir),
        "total_files_generated": total_files_generated,
        "naming_convention": naming_convention,
        "sample_files_names": sample_files_names,
    }
