from collections.abc import Iterable, Sequence
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Self

from networkx import MultiDiGraph as _nxDiGraph

if TYPE_CHECKING:
    from pygraph._adapters.protocols import DiGraphProto
else:
    DiGraphProto = object


class DiGraph[N: Any, E: Any](DiGraphProto[N, E]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if TYPE_CHECKING:
            self._graph = _nxDiGraph[int](*args, **kwargs)
        else:
            self._graph = _nxDiGraph(*args, **kwargs)
        self._edge_index_map = dict[int, tuple[int, int, E]]()
        self._edge_index = 0
        self._node_index_map = dict[int, N]()
        self._node_index = 0

    def edges(self) -> list[E]:
        return [e[2] for e in self._edge_index_map.values()]

    def nodes(self) -> list[N]:
        return list(self._node_index_map.values())

    def add_node(self, obj: N) -> int:
        self._node_index += 1
        self._graph.add_node(self._node_index, object=obj)
        self._node_index_map[self._node_index] = obj
        return self._node_index

    def edge_index_map(self) -> dict[int, tuple[int, int]]:
        return {e_id: (e[0], e[1]) for e_id, e in self._edge_index_map.items()}

    def add_edge(self, parent: int, child: int, edge: E | None = None) -> int:
        self._edge_index += 1
        self._edge_index_map[self._edge_index]
        self._graph.add_edge(parent, child, object=edge)
        return self._edge_index

    def add_nodes_from(self, obj_list: Iterable[N]) -> Sequence[int]:
        obj_list = list(obj_list)
        idx = self._node_index
        self._graph.add_nodes_from(
            (i, {'object': n})
            for i, n in enumerate(obj_list, start=idx + 1)
        )
        ids = list(range(idx, idx + len(obj_list), 1))
        self._node_index_map.update(dict(zip(ids, obj_list, strict=True)))
        self._node_index = ids[-1]
        return ids

    def copy(self) -> Self:
        new = type(self)()
        new._edge_index = self._edge_index
        new._node_index = self._node_index
        new._edge_index_map = deepcopy(self._edge_index_map)
        new._node_index_map = deepcopy(self._node_index_map)
        return new
