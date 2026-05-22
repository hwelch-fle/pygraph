import json
import rustworkx as rx

from typing import Any, Literal, TypedDict, Unpack, overload
from collections.abc import Iterable, Callable, Mapping
from types import MappingProxyType

from .vis import (
    DefaultEdgeOptions, EdgeOptions, EdgeRecord,
    DefaultNodeOptions, NodeOptions, NodeRecord,
    NetworkOptions, DefaultNetworkOptions,
)
from pygraph.vis.physics import (
    BarnesHut, DefaultBarnesHut,
    ForceAtlas2Based, DefaultForceAtlas2Based,
    Repulsion, DefaultRepulsion,
    HierarchicalRepulsion, DefaultHierarchicalRepulsion,
)


__all__ = 'Node', 'Edge', 'Network', 'NodeId', 'EdgeId', 'NetworkData'


type NodeId = str | int
type EdgeId = tuple[NodeId, NodeId]


# Helper to de proxy the defaults 
# types are all wrong becuase we're lying about what the Default* 
# dicts are since MappingProxyType will clear all TypedDict hinting
def _deprox[T: Mapping[str, Any]](o: T) -> T:
    """INTERNAL: Used to turn nested MappingProxyTypes into a dict"""
    deproxed: T = {}      # type: ignore
    for k,v in o.items():
        deproxed[k] = (   # type: ignore
            _deprox(v)    # type: ignore
            if isinstance(v, (dict, MappingProxyType)) 
            else v
        )
    return deproxed


class Node:
    __defaults__ = DefaultNodeOptions
    __slots__ = ('data', '_is_custom')
    
    def __init__(self, id: int | str, **kwargs: Unpack[NodeOptions]) -> None:
        self.data: NodeRecord = {'id': id, 'label': kwargs.get('label') or str(id)}
        self._is_custom = self.__defaults__ is not DefaultNodeOptions
        if self._is_custom:
            self.data.update(_deprox(self.__defaults__)) # type: ignore
        self.data.update(kwargs) # type: ignore
      
    def __getitem__(self, key: str) -> Any:
        return self.data[key] # type: ignore   
    
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
            f'data=<{sorted(set(self.data.keys())-{'id'})}>)'
        )
  
    @property
    def key(self) -> NodeId:
        return self.data['id']
  
    def to_json(self, indent: int=2, sort_keys: bool=True) -> str:
        return json.dumps(self.data, indent=indent, sort_keys=sort_keys)
    
    def set_default(self, *key_filter: str) -> None:
        if key_filter:
            defaults = {k:v for k,v in self.__defaults__.items() if k in key_filter}
        else:
            defaults = _deprox(self.__defaults__)
        if self._is_custom:
            self.data.update(defaults) # type: ignore
        else:
            for k in defaults:
                self.data.pop(k, None)
    
    def set(self, **options: Unpack[NodeOptions]) -> None:
        self.data.update(options) # type: ignore

    @classmethod
    def set_node_defaults(cls, defaults: NodeOptions) -> None:
        cls.__defaults__ = defaults

class Edge:
    __defaults__ = DefaultEdgeOptions
    __slots__ = ('data', '_is_custom',)
    
    def __init__(self, frm: int | str, to: int | str, *, id: str | None = None, **kwargs: Unpack[EdgeOptions]) -> None:
        self.data: EdgeRecord = {'from': frm, 'to': to}
        if id:
            self.data['id'] = id
        self._is_custom = self.__defaults__ is not DefaultEdgeOptions
        if self._is_custom:
            self.data.update(_deprox(self.__defaults__)) # type: ignore
        self.data.update(kwargs) # type: ignore
    
    def __getitem__(self, key: str) -> Any:
        return self.data[key] # type: ignore
    
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
            f'data=<{sorted(set(self.data.keys())-{'from', 'to'})}>)'
        )
     
    @property
    def key(self) -> EdgeId:
        return (self.data['from'], self.data['to'])
    
    def to_json(self, indent: int=2, sort_keys: bool=True) -> str:
        return json.dumps(self.data, indent=indent, sort_keys=sort_keys)
    
    def set_default(self, *key_filter: str) -> None:
        if key_filter:
            defaults = {k:v for k,v in self.__defaults__.items() if k in key_filter}
        else:
            defaults = _deprox(self.__defaults__)
        if self._is_custom:
            self.data.update(defaults) # type: ignore
        else:
            for k in defaults:
                self.data.pop(k, None)
                
    def set(self, **options: Unpack[EdgeOptions]) -> None:
        self.data.update(options) # type: ignore

    @classmethod
    def set_edge_defaults(cls, defaults: EdgeOptions) -> None:
        cls.__defaults__ = defaults

class NetworkData(TypedDict):
    """Serialized json data required for creating visjs Network objects.
    
    Returned by `Network.to_data` and can be used in jinja HTML templates
    """
    nodes: str
    edges: str
    options: str


class Network:
    __defaults__ = DefaultNetworkOptions
    __slots__ = 'options', 'graph', '_directed'
    
    def __init__(self, 
                 ns: Iterable[Node | NodeId] | None = None, 
                 es: Iterable[Edge | EdgeId] | None = None, 
                 **kwargs: Unpack[NetworkOptions]
        ) -> None:
        self.options = _deprox(DefaultNetworkOptions)
        self.options.update(kwargs)
        self.graph = rx.PyDiGraph()
        self.add_nodes_from(ns or [])
        self.add_edges_from(es or [])
        self._directed = False
    
    # Graph Properties
    
    @property
    def nodes(self) -> list[Node]:
        return self.graph.nodes()
    
    @property
    def edges(self) -> list[Edge]:
        return self.graph.edges()
    
    @property
    def node_map(self) -> dict[NodeId, int]:
        _idxs = self.graph.node_indices()
        return {n.key:i for n,i in zip(self.nodes, _idxs)}
    
    @property
    def edge_map(self) -> dict[EdgeId, int]:
        _idxs = self.graph.edge_indices()
        return {e.key:i for e,i in zip(self.edges, _idxs)}
    
    # Graph Manipulators 
    
    def add_edge(self, e: Edge | EdgeId, *, create_nodes: bool = False) -> int | None:
        node_map = self.node_map
        # Cast to Edge
        e = e if isinstance(e, Edge) else Edge(*e[:2])
        
        if create_nodes:
            f,t = e.key
            if f not in node_map: self.add_node(f)
            if t not in node_map: self.add_node(t)
            node_map = self.node_map
        
        if e not in self:
            return self.graph.add_edge(node_map[e['from']], node_map[e['to']], e)
        
    def add_node(self, n: Node | NodeId) -> int | None:
        # Cast to Node
        n = n if isinstance(n, Node) else Node(n)
        if n not in self:
            return self.graph.add_node(n)
        
    def add_edges_from(self, es: Iterable[Edge | EdgeId], *, create_nodes: bool = False) -> list[int]:
        node_map = self.node_map
        existing = set[EdgeId](self.edge_map)
        
        if create_nodes:
            # Store es since it could be a generator/iterator
            es = [e if isinstance(e, Edge) else Edge(*e[:2]) for e in es]
            self.add_nodes_from(
                n for e in es for n in e.key if n not in node_map
            )
            node_map = self.node_map

        return self.graph.add_edges_from(
            (node_map[e['from']], node_map[e['to']], e) for _ in es
            # Cast to Edge
            if (e := _) and isinstance(e, Edge) 
            or (e := Edge(*e))
            # Prevent Duplicate
            and e.key not in existing 
            and existing.add(e.key) is None
        )
    
    def add_nodes_from(self, ns: Iterable[Node | NodeId]) -> list[int]:
        existing = set[NodeId](self.node_map)
        return list(
            self.graph.add_nodes_from(
                n for _ in ns
                # Cast to Node
                if (n := _) and isinstance(n, Node) 
                or (n := Node(n))
                # Prevent Duplicate
                and n.key not in existing
                and existing.add(n.key) is None
            )
        )

    def remove_node(self, n: Node) -> None:
        self.graph.remove_node(self.node_map[n.key])
    
    def remove_edge(self, e: Edge) -> None:
        self.graph.remove_edge_from_index(self.edge_map[e.key])
    
    def clear(self) -> None:
        self.graph.clear()
    
    def clear_edges(self) -> None:
        self.graph.clear_edges()
    
    def adj_list(self, node: Node | NodeId) -> dict[Node, Edge]:
        node = node.key if isinstance(node, Node) else node
        adj = self.graph.adj(self.node_map[node])
        return {self[nd]: adj[nd] for nd in adj}
    
    # Dunder Overrides
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(N=|{len(self.nodes)}|, E=|{len(self.edges)}|)'
   
    @overload
    def __getitem__(self, key: NodeId) -> Node: ...
    @overload
    def __getitem__(self, key: EdgeId) -> Edge: ...
    def __getitem__(self, key: NodeId | EdgeId) -> Node | Edge:
        if isinstance(key, (str, int)):
            return self.graph[self.node_map[key]]
        elif isinstance(key, tuple) and len(key) == 2: # type: ignore
            return self.graph.get_edge_data_by_index(self.edge_map[key])
        raise KeyError(f'Invalid Edge/Node Id: {key}')
    
    @overload
    def get[D](self, key: NodeId, default: D = None) -> Node | D: ...
    @overload
    def get[D](self, key: EdgeId, default: D = None) -> Edge | D: ...
    def get[D](self, key: NodeId | EdgeId, default: D = None) -> Any | D:
        try:
            return self[key]
        except KeyError:
            return default
    
    @overload
    def __setitem__(self, key: NodeId, value: NodeOptions) -> None: ...
    @overload
    def __setitem__(self, key: EdgeId, value: EdgeOptions) -> None: ...
    def __setitem__(self, key: NodeId | EdgeId, value: Any) -> None:
        if isinstance(key, (str | int)):
            node = self[key]
            node.data.update(value)
            key = self.node_map[key]
            self.graph[key] = node
        elif isinstance(key, tuple) and len(key) == 2: # type: ignore
            edge = self[key]
            edge.data.update(value)
            key = self.edge_map[key]
            self.graph.update_edge_by_index(key, edge)
        raise KeyError(f'Invalid Edge/Node Id: {key}')
    
    def __delitem__(self, item: Any):
        if isinstance(item, (Node, Edge)):
            item = item.key
        
        if isinstance(item, (int | str)):
            self.graph.remove_node(self.node_map[item])
        elif isinstance(item, tuple) and len(item) == 2: # type: ignore
            self.graph.remove_edge_from_index(self.edge_map[item])
        raise KeyError(f'Invalid Edge/Node Id: {item}')
    
    def __contains__(self, item: Any) -> bool:
        if isinstance(item, (Node, Edge)):
            item = item.key
        
        if isinstance(item, (str | int)):
            return item in self.node_map
        elif isinstance(item, tuple) and len(item) == 2: # type: ignore
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
            node_attr = lambda n: {'label': f'{n.data.get('label')}'}
        if edge_attr is None and default_label:
            edge_attr = lambda e: {'label': f'{e.data.get('label')}'}
        return self.graph.to_dot(node_attr, edge_attr, graph_attr)
    
    def get_data(self) -> NetworkData:
        return {
            'nodes': json.dumps([n.data for n in self.nodes]),
            'edges': json.dumps([e.data for e in self.edges]),
            'options': json.dumps(self.options),
        }
