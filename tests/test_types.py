from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    try:
        from typing import assert_type  # type: ignore
    except ImportError:
        def assert_type(*args: Any, **kwargs: Any) -> bool:
            return True

    from pygraph import (
        Edge,
        EdgeId,
        EdgeOptions,
        EdgeRecord,
        Network,
        NetworkData,
        NetworkOptions,
        Node,
        NodeId,
        NodeOptions,
        NodeRecord,
    )

    def test_network_attributes():
        nx = Network()
        assert_type(nx.nodes, list[Node])
        assert_type(nx.edges, list[Edge])
        assert_type(nx.node_map, dict[NodeId, int])
        assert_type(nx.edge_map, dict[EdgeId, int])
        assert_type(nx.options, NetworkOptions)
        assert_type(nx.get_data(), NetworkData)

    def test_edge_attributes():
        e = Edge(0, 0)
        assert_type(e.key, EdgeId)
        assert_type(e.data, EdgeRecord)
        e.set(**EdgeOptions())

    def test_node_attributes():
        n = Node(0)
        assert_type(n.key, NodeId)
        assert_type(n.data, NodeRecord)
        n.set(**NodeOptions())
