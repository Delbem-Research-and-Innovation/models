"""Write phylogenetic trees in Newick format."""

from pathlib import Path

from damicore_tree_builder.neighbor_joining import Clade, Tree


class NewickWriter:
    """Writes a phylogenetic tree to a Newick file."""

    def __init__(self, output_path: str) -> None:
        self.output_path = Path(output_path)

    def write(self, tree: Tree | None) -> Path:
        """Write the tree and return the generated file path."""
        if tree is None:
            raise ValueError("Tree cannot be None.")

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(self.to_newick(tree), encoding="utf-8")

        return self.output_path

    def to_newick(self, tree: Tree) -> str:
        return f"{self._format_clade(tree.root)};\n"

    def _format_clade(self, clade: Clade) -> str:
        label = self._escape_name(clade.name) if clade.name is not None else ""
        length = f":{clade.branch_length:.10g}"

        if clade.children:
            children = ",".join(self._format_clade(child) for child in clade.children)
            return f"({children}){label}{length}"

        return f"{label}{length}"

    def _escape_name(self, name: str) -> str:
        if name and all(character not in name for character in " \t\n\r():;,[]'"):
            return name

        return "'" + name.replace("'", "''") + "'"
