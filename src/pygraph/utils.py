import itertools
from collections.abc import Iterable
from copy import deepcopy
from typing import (
    Any,
    Unpack,
)

import jinja2
import rustworkx as rx

from pygraph.pygraph import (
    Edge,
    Network,
    Node,
    NodeId,
)
from pygraph.vis import (
    EdgeOptions,
)


def shortest_paths(nx: Network, fr: Node | NodeId, to: Node | NodeId, *, directed: bool = False) -> list[list[Edge]]:
    """Highlight the shortest path between two nodes in the network

    Args:
        nx: The network object to traverse
        fr: The start Node
        to: The end Node
        undirected: Ignore directionality of edges (default: False)

    Returns:
        A nested list of edge objects that contains all shortest paths

    Example:
        ```python
        >>> shortest_paths(nx, 'Node 1', 'Node 10', undirected=True)
        [[Edge(...), Edge(...), ...], [Edge(...), Edge(...), ...], ...]
        ```
    """
    fr = nx.node_map[fr.key if isinstance(fr, Node) else fr]
    to = nx.node_map[to.key if isinstance(to, Node) else to]
    shortest = rx.digraph_all_shortest_paths(
        nx.graph, fr, to, as_undirected = not directed
    )
    return [[nx[edge] for edge in itertools.pairwise(path)] for path in shortest]


def style_edges(edges: Iterable[Edge], **options: Unpack[EdgeOptions]) -> list[Edge]:
    """Apply a style to all supplied Edges

    Args:
        edges: An Iterable of Edges that you want to apply a uniform style to
        **options: EdgeOptions (see `vis.modules.edge.EdgeOptions`)

    Return:
        A list of the modified edges
    """
    return [edge.set(**options) or edge for edge in edges]


def style_nodes(nodes: Iterable[Node], **options: Unpack[EdgeOptions]) -> list[Node]:
    """Apply a style to all supplied Nodes

    Args:
        Nodes: An Iterable of Nodes that you want to apply a uniform style to
        **options: Node (see `vis.modules.node.NodeOptions`)

    Return:
        A list of the modified edges
    """
    return [node.set(**options) or node for node in nodes] # type: ignore


def get_neighborhood(nx: Network, root: Node | NodeId, level: int = 1, *, copy: bool = False) -> Network:
    """Get a new Network that represents the neighborhood of a specified Node

    Args:
        nx: The Network to find a neighborhood in
        root: The root node of the neighborhood
        level: The number of levels to include in the neighborhood
        copy: Create new Edges and Nodes so the networks are unlinked (default: False)

    Returns:
        A new Network filtered on the root node and level

    Note:
        A Neighborhood will create a new Network, but the edges and nodes will be references
        to the originals, meaning updates to either will be shared. Set the `copy` flag to
        create a deep copy of all network elements in the new Network.
    """
    if level < 0:
        raise ValueError(
            f'Level must be a positive integer (or zero for only the root node), got {level}'
        )

    if not isinstance(root, Node):
        root = nx[root]

    neighborhood = Network([deepcopy(root) if copy else root])
    while level > 0:
        for neighbors in (nx.adj_list(n) for n in neighborhood.nodes):
            neighborhood.add_nodes_from(
                deepcopy(node) if copy else node for node in neighbors.keys()
            )
            neighborhood.add_edges_from(
                deepcopy(edge) if copy else edge for edge in neighbors.values()
            )
        level -= 1
    return neighborhood


def kevin_bacon(nx: Network, node: Node | NodeId, *, copy: bool = False) -> Network:
    """Shorthand for a level 7 neighborhood"""
    return get_neighborhood(nx, node, 7, copy=copy)


def to_html(nx: Network, template: jinja2.Template, **kwargs: Any) -> str:
    """Export the network to an HTML template

    The supplied template *MUST* accept `nodes`, `edges`, and `options` values that
    are used to build the visjs Network object

    (see [visjs docs](https://visjs.github.io/vis-network/docs/network/) click "Show the getting started")

    Args:
        nx: The Network object to render
        template: A Jinja2 Template object that accepts `nodes`, `edges`, and `options` for a vis.Network() object
        **kwargs: Any additional tempalte data that you wish to pass to the template renderer

    Returns:
        A string value with the HTML required to render the network
    """
    nx_data = nx.get_data()
    kwargs.update(nx_data)
    return template.render(**kwargs)
