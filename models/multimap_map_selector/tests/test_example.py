import json
from pathlib import Path

from multimap_map_selector import RecommenderStrategy, recommend_visualization_spec


def test_recommend_visualization_spec_for_fixture(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[3]
    source_file = (
        root / "models" / "fixtures" / "dataset-seade-pop-age" / "raw-dataset-seade-pop-age.csv"
    )

    result = recommend_visualization_spec(
        source_file,
        RecommenderStrategy(target_library="geovis", fallback_map="base_map"),
        output_directory=tmp_path,
    )

    assert result.status == "success"
    assert result.visualization_spec["engine"] == "maplibre"
    assert result.visualization_spec["layer_type"] == "choropleth"
    assert result.visualization_spec["data_points_mapped"] > 0
    assert result.output_spec_path

    output_path = Path(result.output_spec_path)
    assert output_path.exists()
    spec = json.loads(output_path.read_text(encoding="utf-8"))
    assert spec["engine"] == "maplibre"
    assert spec["value_column"] == "populacao"
    assert spec["join_key"] == "cod_distr"


def test_recommend_visualization_spec_fails_when_no_spatial_column(tmp_path: Path) -> None:
    source_file = tmp_path / "flat.csv"
    source_file.write_text("year,value\n2020,100\n2021,120\n", encoding="utf-8")

    result = recommend_visualization_spec(
        source_file,
        RecommenderStrategy(target_library="geovis", fallback_map="base_map"),
    )

    assert result.status == "failure"
    assert "spatial" in result.visualization_spec["reason"].lower()
    assert result.output_spec_path == ""
