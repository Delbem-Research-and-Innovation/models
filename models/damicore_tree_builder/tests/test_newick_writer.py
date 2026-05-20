from pathlib import Path

import pytest

from damicore_tree_builder.neighbor_joining import Clade, Tree
from damicore_tree_builder.newick_writer import NewickWriter


@pytest.mark.unit
def test_writes_newick_file(tmp_path: Path) -> None:
    output_path = tmp_path / "tree.newick"
    tree = Tree(
        root=Clade(
            children=[
                Clade(name="A", branch_length=1.0),
                Clade(name="B value", branch_length=2.5),
            ]
        )
    )

    generated_path = NewickWriter(str(output_path)).write(tree)

    assert generated_path == output_path
    assert output_path.read_text(encoding="utf-8") == "(A:1,'B value':2.5):0;\n"


@pytest.mark.unit
def test_rejects_missing_tree(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Tree cannot be None"):
        NewickWriter(str(tmp_path / "tree.newick")).write(None)
