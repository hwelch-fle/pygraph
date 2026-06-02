import json
from collections.abc import (
    Callable,
    Iterable,
    Mapping,
)
from copy import deepcopy
from typing import (
    Any,
    Literal,
    TypedDict,
    TypeGuard,
    Unpack,
    overload,
)

import rustworkx as rx

from pygraph.vis.physics import (
    BarnesHut,
    DefaultBarnesHut,
    DefaultForceAtlas2Based,
    DefaultHierarchicalRepulsion,
    DefaultRepulsion,
    ForceAtlas2Based,
    HierarchicalRepulsion,
    Repulsion,
)

from .vis import (
    DefaultEdgeOptions,
    DefaultNetworkOptions,
    DefaultNodeOptions,
    EdgeOptions,
    EdgeRecord,
    NetworkOptions,
    NodeOptions,
    NodeRecord,
)

__all__ = (
    'Edge',
    'EdgeId',
    'EdgeOptions',
    'EdgeOptions',
    'EdgeRecord',
    'Network',
    'NetworkData',
    'NetworkOptions',
    'Node',
    'NodeId',
    'NodeOptions',
    'NodeRecord',
)


type NodeId = str | int
type EdgeId = tuple[NodeId, NodeId]


def is_mapping(obj: Mapping[Any, Any] | Any) -> TypeGuard[Mapping[Any, Any]]:
    return isinstance(obj, Mapping)


# Helper to de proxy the defaults
# types are all wrong becuase we're lying about what the Default*
# dicts are since MappingProxyType will clear all TypedDict hinting
def deprox[T](o: T) -> T:
    """INTERNAL: Used to turn nested MappingProxyTypes into a dict"""
    deproxed: dict[Any, Any] = {}
    assert is_mapping(o)
    for k, v in o.items():
        if is_mapping(v):
            deproxed[k] = deprox(v)
        else:
            deproxed[k] = deepcopy(v)
    return deproxed  # type: ignore


class Node:
    __defaults__ = DefaultNodeOptions
    __slots__ = ('_is_custom', 'data')

    def __init__(self, id: int | str, **kwargs: Unpack[NodeOptions]) -> None:
        self.data: NodeRecord = {'id': id, 'label': kwargs.get('label') or str(id)}
        self._is_custom = self.__defaults__ is not DefaultNodeOptions
        if self._is_custom:
            self.data.update(deprox(self.__defaults__))  # type: ignore
        self.data.update(kwargs)  # type: ignore

    def __getitem__(self, key: str) -> Any:
        return self.data[key]  # type: ignore

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get[D](self, key: str, default: D = None) -> Any | D:
        try:
            return self[key]
        except KeyError:
            return default

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.data['id']}, '
            f'data=<{sorted(set(self.data.keys()) - {'id'})}>)'
        )

    @property
    def key(self) -> NodeId:
        return self.data['id']

    def to_json(self, indent: int = 2, sort_keys: bool = True) -> str:
        return json.dumps(self.data, indent=indent, sort_keys=sort_keys)

    def set_default(self, *key_filter: str) -> None:
        if key_filter:
            defaults = {k: v for k, v in self.__defaults__.items() if k in key_filter}
        else:
            defaults = deprox(self.__defaults__)
        if self._is_custom:
            self.data.update(defaults)  # type: ignore
        else:
            for k in defaults:
                self.data.pop(k, None)

    def set(self, **options: Unpack[NodeOptions]) -> None:
        self.data.update(options)  # type: ignore

    @classmethod
    def set_node_defaults(cls, defaults: NodeOptions) -> None:
        cls.__defaults__ = defaults


class Edge:
    __defaults__ = DefaultEdgeOptions
    __slots__ = ('_is_custom', 'data')

    def __init__(self, frm: int | str, to: int | str, *, id: str | None = None, **kwargs: Unpack[EdgeOptions]) -> None:
        self.data: EdgeRecord = {'from': frm, 'to': to}
        if id:
            self.data['id'] = id
        self._is_custom = self.__defaults__ is not DefaultEdgeOptions
        if self._is_custom:
            self.data.update(deprox(self.__defaults__))  # type: ignore
        self.data.update(kwargs)  # type: ignore

    def __getitem__(self, key: str) -> Any:
        return self.data[key]  # type: ignore

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get[D](self, key: str, default: D = None) -> Any | D:
        try:
            return self[key]
        except KeyError:
            return default

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'from={self.data['from']}, to={self.data['to']}, '
            f'data=<{sorted(set(self.data.keys()) - {'from', 'to'})}>)'
        )

    @property
    def key(self) -> EdgeId:
        return (self.data['from'], self.data['to'])

    def to_json(self, indent: int = 2, sort_keys: bool = True) -> str:
        return json.dumps(self.data, indent=indent, sort_keys=sort_keys)

    def set_default(self, *key_filter: str) -> None:
        if key_filter:
            defaults = {k: v for k, v in self.__defaults__.items() if k in key_filter}
        else:
            defaults = deprox(self.__defaults__)
        if self._is_custom:
            self.data.update(defaults)  # type: ignore
        else:
            for k in defaults:
                self.data.pop(k, None)

    def set(self, **options: Unpack[EdgeOptions]) -> None:
        self.data.update(options)  # type: ignore

    @classmethod
    def set_edge_defaults(cls, defaults: EdgeOptions) -> None:
        cls.__defaults__ = defaults


class NetworkData(TypedDict):
    """Serialized json data required for creating visjs Network objects.

    Returned by `Network.to_data` and can be used in jinja HTML templates
    """
    nodes: list[NodeRecord]
    edges: list[EdgeRecord]
    options: NetworkOptions


class Network:
    __defaults__ = DefaultNetworkOptions
    __slots__ = 'graph', 'options'

    def __init__(self,
                 ns: Iterable[Node | NodeId] | None = None,
                 es: Iterable[Edge | EdgeId] | None = None,
                 **kwargs: Unpack[NetworkOptions]
        ) -> None:
        self.options: NetworkOptions = deprox(DefaultNetworkOptions)
        self.options.update(kwargs)
        self.graph = rx.PyDiGraph()
        self.add_nodes_from(ns or [])
        self.add_edges_from(es or [])

    # Graph Properties

    @property
    def nodes(self) -> list[Node]:
        return self.graph.nodes()

    @property
    def edges(self) -> list[Edge]:
        return self.graph.edges()

    @property
    def node_map(self) -> dict[NodeId, int]:
        return {
            n.key: i
            for n, i
            in zip(self.nodes, self.graph.node_indices(), strict=True)
        }

    @property
    def edge_map(self) -> dict[EdgeId, int]:
        return {
            e.key: i
            for e, i
            in zip(self.edges, self.graph.edge_indices(), strict=True)
        }

    # Graph Manipulators

    def _cast_edge(self, e: Edge | EdgeId) -> Edge:
        return e if isinstance(e, Edge) else Edge(*e[:2])

    def _cast_node(self, n: Node | NodeId) -> Node:
        return n if isinstance(n, Node) else Node(n)

    def _extract_nodes(self, es: Iterable[Edge]) -> Iterable[Node]:
        yield from (self._cast_node(n) for e in es for n in e.key)

    def add_edge(self, e: Edge | EdgeId, *, create_nodes: bool = False) -> int | None:
        if e in self:
            return

        node_map = self.node_map
        e = self._cast_edge(e)
        fr, to = e.key

        if create_nodes:
            node_map.update(dict(zip(e.key, self.add_nodes_from(e.key), strict=True)))

        return self.graph.add_edge(node_map[fr], node_map[to], e)

    def add_node(self, n: Node | NodeId) -> int | None:
        if n in self:
            return

        return self.graph.add_node(self._cast_node(n))

    def add_edges_from(self, es: Iterable[Edge | EdgeId], *, create_nodes: bool = False) -> list[int]:
        existing = set(self.edge_map.keys())
        es = tuple(self._cast_edge(e) for e in es if e not in existing)

        if create_nodes:
            self.add_nodes_from(self._extract_nodes(es))

        node_map = self.node_map
        return self.graph.add_edges_from(
            (node_map[key[0]], node_map[key[1]], edge)
            for edge in map(self._cast_edge, es)
            if (key := edge.key)
            and key not in existing
            and existing.add(key) is None
        )

    def add_nodes_from(self, ns: Iterable[Node | NodeId]) -> list[int]:
        existing = set(self.node_map)

        return list(
            self.graph.add_nodes_from(
                node for node in map(self._cast_node, ns)
                if node.key not in existing
                and existing.add(node.key) is None
            )
        )

    def remove_node(self, n: Node, *, retain_edges: bool = False) -> None:
        if retain_edges:
            self.graph.remove_node_retain_edges(self.node_map[n.key])
        else:
            self.graph.remove_node(self.node_map[n.key])

    def remove_nodes_from(self, ns: Iterable[Node]) -> None:
        node_map = self.node_map
        self.graph.remove_nodes_from(
            node_map[n.key] for n in map(self._cast_node, ns)
        )

    def remove_edge(self, e: Edge) -> None:
        edge_map = self.edge_map
        if e.key not in edge_map:
            return
        self.graph.remove_edge_from_index(edge_map[e.key])

    def remove_edges_from(self, es: Iterable[Edge]) -> None:
        node_map = self.node_map
        self.graph.remove_edges_from(
            (node_map[e.key[0]], node_map[e.key[1]]) for e in map(self._cast_edge, es)
        )

    def clear(self) -> None:
        self.graph.clear()

    def clear_edges(self) -> None:
        self.graph.clear_edges()

    def adj_list(self, node: Node | NodeId) -> dict[Node, Edge]:
        node = node.key if isinstance(node, Node) else node
        adj = self.graph.adj(self.node_map[node])
        return {self.graph[nd]: adj[nd] for nd in adj}

    # Dunder Overrides

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(N=|{len(self.nodes)}|, E=|{len(self.edges)}|)'

    @overload
    def __getitem__(self, key: NodeId | Node) -> Node: ...
    @overload
    def __getitem__(self, key: EdgeId | Edge) -> Edge: ...
    def __getitem__(self, key: NodeId | Node | EdgeId | Edge) -> Node | Edge:
        key = key.key if isinstance(key, (Node, Edge)) else key

        if isinstance(key, (str, int)):
            return self.graph[self.node_map[key]]
        elif isinstance(key, tuple) and len(key) == 2:  # type: ignore
            return self.graph.get_edge_data_by_index(self.edge_map[key])

        raise KeyError(f'Invalid Edge/Node Id: {type(key)}:{key}')

    @overload
    def get[D](self, key: NodeId | Node, default: D = None) -> Node | D: ...
    @overload
    def get[D](self, key: EdgeId | Edge, default: D = None) -> Edge | D: ...
    def get[D](self, key: NodeId | Node | EdgeId | Edge, default: D = None) -> Any | D:
        try:
            return self[key]
        except KeyError:
            return default

    @overload
    def __setitem__(self, key: NodeId | Node, value: NodeOptions) -> None: ...
    @overload
    def __setitem__(self, key: EdgeId | Edge, value: EdgeOptions) -> None: ...
    def __setitem__(self, key: Any, value: Any) -> None:
        key = key.key if isinstance(key, (Node, Edge)) else key

        if isinstance(key, (str, int)):
            self[key].data.update(value)
        elif isinstance(key, tuple) and len(key) == 2:  # type: ignore
            self[key].data.update(value)
        else:
            raise KeyError(f'Invalid Edge/Node Id: {key}')

    def __delitem__(self, item: NodeId | Node | EdgeId | Edge):
        if isinstance(item, (Node, Edge)):
            item = item.key

        if isinstance(item, (str, int)):
            self.graph.remove_node(self.node_map[item])
        elif isinstance(item, tuple) and len(item) == 2:  # type: ignore
            self.graph.remove_edge_from_index(self.edge_map[item])
        else:
            raise KeyError(f'Invalid Edge/Node Id: {type(item)}:{item}')

    def __contains__(self, item: NodeId | Node | EdgeId | Edge) -> bool:
        item = item.key if isinstance(item, (Node, Edge)) else item

        if isinstance(item, (str, int)):
            return item in self.node_map
        elif isinstance(item, tuple) and len(item) == 2:  # type: ignore
            return item in self.edge_map

        return False

    # Network Modifiers

    def directed(self, val: bool = True) -> None:
        if 'edges' not in self.options:
            self.options['edges'] = {}
        self.options['edges'].update({'arrows': {'to': {'enabled': val}}})

    def barnes_hut(self, **barnes_hut: Unpack[BarnesHut]) -> None:
        if not barnes_hut:
            barnes_hut = DefaultBarnesHut
        if 'physics' not in self.options:
            self.options['physics'] = {}
        self.options['physics']['barnesHut'] = barnes_hut

    def force_atlas_2_based(self, **force_atlas_2_based: Unpack[ForceAtlas2Based]) -> None:
        if not force_atlas_2_based:
            force_atlas_2_based = DefaultForceAtlas2Based
        if 'physics' not in self.options:
            self.options['physics'] = {}
        self.options['physics']['forceAtlas2Based'] = force_atlas_2_based

    def repulsion(self, **repulsion: Unpack[Repulsion]) -> None:
        if not repulsion:
            repulsion = DefaultRepulsion
        if 'physics' not in self.options:
            self.options['physics'] = {}
        self.options['physics']['repulsion'] = repulsion

    def hrepulsion(self, **hrepulsion: Unpack[HierarchicalRepulsion]) -> None:
        if not hrepulsion:
            hrepulsion = DefaultHierarchicalRepulsion
        if 'physics' not in self.options:
            self.options['physics'] = {}
        self.options['physics']['hierarchicalRepulsion'] = hrepulsion

    def solver(self, solver: Literal['barnesHut', 'repulsion', 'hierarchicalRepulsion', 'forceAtlas2Based']) -> None:
        if 'physics' not in self.options:
            self.options['physics'] = {}
        self.options['physics']['solver'] = solver

    # Export Methods

    def to_dot(self,
               node_attr: Callable[[Node], dict[str, str]] | None = None,
               edge_attr: Callable[[Edge], dict[str, str]] | None = None,
               graph_attr: dict[str, str] | None = None,
               *,
               default_label: bool = True,
        ) -> str:
        """Export the Network to a DOT string

        Args:
            node_attr: A function that extracts attributes in the form `dict[str, str]` for a Node
            edge_attr: A function that extracts attributes in the form `dict[str, str]` for an Edge
            graph_attr: A `dict[str, str]` mapping of graph level attributes
            default_label: If set, the `label` attribute will be assigned
                for each Node and Edge if corresponding `*_attr` function is not set (default: `True`)

        Returns:
            A DOT string for the Network with the requested attributes
            (see [graphviz attributes](https://www.graphviz.org/doc/info/attrs.html))
        """
        if node_attr is None and default_label:
            def _node_attr(n: Node):
                return {'label': f'{n.data.get('label')}'}
            node_attr = _node_attr

        if edge_attr is None and default_label:
            def _edge_attr(e: Edge):
                return {'label': f'{e.data.get('label')}'}
            edge_attr = _edge_attr

        return self.graph.to_dot(node_attr, edge_attr, graph_attr)

    def to_json(self, *, indent: int = 2, sort_keys: bool = True, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=sort_keys, **kwargs)

    def to_dict(self) -> NetworkData:
        return {
            'nodes': [n.data for n in self.nodes],
            'edges': [e.data for e in self.edges],
            'options': self.options,
        }
