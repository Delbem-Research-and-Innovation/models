from __future__ import annotations

from dataclasses import dataclass

"""Build phylogenetic trees with the Neighbor-Joining algorithm."""


@dataclass
class Clade:
    """A tree node with an optional branch length from its parent."""

    name: str | None = None
    branch_length: float = 0.0
    children: list[Clade] | None = None

    def __post_init__(self) -> None:
        if self.children is None:
            self.children = []

    @property
    def is_terminal(self) -> bool:
        assert self.children is not None
        return not self.children


@dataclass
class Tree:
    """Small tree wrapper exposing the methods used by the CLI contract."""

    root: Clade

    def get_terminals(self) -> list[Clade]:
        return [clade for clade in self._walk(self.root) if clade.is_terminal]

    def get_nonterminals(self) -> list[Clade]:
        return [clade for clade in self._walk(self.root) if not clade.is_terminal]

    def _walk(self, clade: Clade) -> list[Clade]:
        clades = [clade]
        for child in clade.children or []:
            clades.extend(self._walk(child))
        return clades


class NeighborJoining:
    """Builds a tree from a full square distance matrix."""

    names: list[str]
    matrix: list[list[float]]

    def __init__(self, names: list[str], matrix: list[list[float]]) -> None:
        self.names = names
        self.matrix = matrix

    def build_tree(self) -> Tree:
        """Build a Neighbor-Joining tree from the configured distances."""
        self._validate_input()

        active_nodes: list[str] = list(self.names)
        clades: dict[str, Clade] = {name: Clade(name=name) for name in self.names}
        distances: dict[frozenset[str], float] = self._initial_distances()
        next_internal_id = 1

        while len(active_nodes) > 2:
            left, right = self._select_pair(active_nodes, distances)
            new_node: str = f"Inner{next_internal_id}"
            next_internal_id += 1

            left_length, right_length = self._branch_lengths(left, right, active_nodes, distances)
            clades[left].branch_length = left_length
            clades[right].branch_length = right_length
            clades[new_node] = Clade(children=[clades[left], clades[right]])

            for other in active_nodes:
                if other in {left, right}:
                    continue
                distances[frozenset((new_node, other))] = (
                    self._distance(left, other, distances)
                    + self._distance(right, other, distances)
                    - self._distance(left, right, distances)
                ) / 2.0

            active_nodes = [node for node in active_nodes if node not in {left, right}]
            active_nodes.append(new_node)

        left, right = active_nodes
        final_distance = self._distance(left, right, distances) / 2.0
        clades[left].branch_length = final_distance
        clades[right].branch_length = final_distance

        return Tree(root=Clade(children=[clades[left], clades[right]]))

    def _validate_input(self) -> None:
        if not self.names:
            raise ValueError("The names list cannot be empty.")

        if len(set(self.names)) != len(self.names):
            raise ValueError("The names list cannot contain duplicates.")

        if not self.matrix:
            raise ValueError("The distance matrix cannot be empty.")

        if len(self.names) != len(self.matrix):
            raise ValueError("The number of names must match the number of matrix rows.")

        for row in self.matrix:
            if len(row) != len(self.names):
                raise ValueError(
                    "The distance matrix must be square and match the number of names."
                )

        if len(self.names) < 3:
            raise ValueError("Neighbor-Joining requires at least 3 elements to build a tree.")

    def _initial_distances(self) -> dict[frozenset[str], float]:
        distances: dict[frozenset[str], float] = {}
        for row_index, left in enumerate(self.names):
            for column_index, right in enumerate(self.names):
                if row_index < column_index:
                    distances[frozenset((left, right))] = float(
                        self.matrix[row_index][column_index]
                    )
        return distances

    def _select_pair(
        self, active_nodes: list[str], distances: dict[frozenset[str], float]
    ) -> tuple[str, str]:
        node_count = len(active_nodes)
        total_distances = {
            node: sum(
                self._distance(node, other, distances) for other in active_nodes if other != node
            )
            for node in active_nodes
        }

        best_pair: tuple[str, str] | None = None
        best_score: float | None = None
        for left_index, left in enumerate(active_nodes):
            for right in active_nodes[left_index + 1 :]:
                score = (
                    (node_count - 2) * self._distance(left, right, distances)
                    - total_distances[left]
                    - total_distances[right]
                )
                if best_score is None or score < best_score:
                    best_score = score
                    best_pair = (left, right)

        if best_pair is None:
            raise ValueError("Could not select a pair for Neighbor-Joining.")
        return best_pair

    def _branch_lengths(
        self, left: str, right: str, active_nodes: list[str], distances: dict[frozenset[str], float]
    ) -> tuple[float, float]:
        node_count = len(active_nodes)
        left_total = sum(
            self._distance(left, other, distances) for other in active_nodes if other != left
        )
        right_total = sum(
            self._distance(right, other, distances) for other in active_nodes if other != right
        )
        pair_distance = self._distance(left, right, distances)
        delta = (left_total - right_total) / (node_count - 2)

        return (pair_distance + delta) / 2.0, (pair_distance - delta) / 2.0

    def _distance(self, left: str, right: str, distances: dict[frozenset[str], float]) -> float:
        if left == right:
            return 0.0
        return distances[frozenset((left, right))]
