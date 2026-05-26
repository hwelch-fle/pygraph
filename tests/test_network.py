from string import (
    ascii_letters,
    ascii_lowercase,
)

import pytest

from pygraph import Network
from pygraph.vis.edge import EdgeOptions
from pygraph.vis.node import NodeOptions


def test_network_init_ints(subtests: pytest.Subtests):
    nx = Network(range(10), [(0,1), (1,2), (1,3)])

    with subtests.test('Test Edge/Node containment'):
        assert 0 in nx
        assert (0,1) in nx

    with subtests.test('Test nodes/edges property length'):
        assert len(nx.nodes) == 10
        assert len(nx.edges) == 3

    with subtests.test(
        'Test len(node_map) == len(nodes) '
        'and len(edge_map) == len(edges)'
    ):
        assert len(nx.node_map) == len(nx.nodes)
        assert len(nx.edge_map) == len(nx.edges)


def test_network_init_strings(subtests: pytest.Subtests):
    nx = Network(ascii_letters)
    nx.add_edges_from((letter, letter.upper()) for letter in ascii_lowercase)

    assert 'a' in nx
    assert ('a', 'A') in nx

    assert len(nx.node_map) == len(nx.nodes)
    assert len(nx.edge_map) == len(nx.edges)


def test_network_duplicate_prevention():
    nx = Network([1,1,1], [(1,1), (1,1), (1,1)])
    nx.add_nodes_from(1 for _ in range(10))
    nx.add_node(1)
    assert len(nx.nodes) == 1
    nx.add_edges_from((1,1) for _ in range(10))
    nx.add_edge((1,1))
    assert len(nx.edges) == 1


def test_network_clear():
    nx = Network(range(10), [(i,j) for i in range(10) for j in range(10)])
    assert len(nx.nodes) == 10
    assert len(nx.edges) == 100
    nx.clear()
    assert len(nx.nodes) == 0
    assert len(nx.edges) == 0


def test_network_clear_edges():
    nx = Network(range(10), [(i,j) for i in range(10) for j in range(10)])
    assert len(nx.nodes) == 10
    assert len(nx.edges) == 100
    nx.clear_edges()
    assert len(nx.nodes) == 10
    assert len(nx.edges) == 0


def test_network_add_bad_edge(subtests: pytest.Subtests):
    nx = Network(range(10))

    with subtests.test('Test Non-Existent Nodes'):
        with pytest.raises(KeyError):
            nx.add_edge((10,11))

    with subtests.test('Test Edge tuple > 2'):
        # with pytest.raises(TypeError):
        nx.add_edge((1,2,3)) # type: ignore


def test_add_edge_create_nodes():
    nx = Network()
    nx.add_edge((1,2), create_nodes=True)
    assert len(nx.nodes) == 2
    assert 1 in nx
    assert 2 in nx


def test_add_edges_create_nodes():
    nx = Network()
    nx.add_edges_from(
        zip(range(10), reversed(range(10)), strict=True), create_nodes=True
    )
    assert len(nx.nodes) == 10
    assert len(nx.edges) == 10


def test_adj_list():
    nx = Network(range(10))
    nx.add_edges_from((0,i) for i in range(10))
    assert len(nx.adj_list(0)) == 10
    assert len(nx.adj_list(9)) == 1


def test_getitem(subtests: pytest.Subtests):
    nx = Network(range(10), zip(range(10), reversed(range(10)), strict=True))

    with subtests.test('Test get Node'):
        assert nx[0] == nx.graph.get_node_data(
            nx.node_map[0]
        )

    with subtests.test('Test get Edge'):
        assert nx[0,9] == nx.graph.get_edge_data(
            nx.node_map[0], nx.node_map[9]
        )


def test_setitem(subtests: pytest.Subtests):
    nx = Network(range(10), zip(range(10), reversed(range(10)), strict=True))

    with subtests.test('Test set Node'):
        nx[0] = NodeOptions(color='UPDATED')
        assert nx[0].data.get('color') == 'UPDATED'
        nx[0].set_default('color')
        assert nx[0].data.get('color') != 'UPDATED'

    with subtests.test('Test set Edge'):
        nx[0,9] = EdgeOptions(color='UPDATED')
        assert nx[0,9].data.get('color') == 'UPDATED'
        nx[0,9].set_default('color')
        assert nx[0,9].data.get('color') != 'UPDATED'


def test_delitem(subtests: pytest.Subtests):
    nx = Network(range(10), zip(range(10), reversed(range(10)), strict=True))

    with subtests.test('Test del Node'):
        assert 0 in nx
        del nx[0]
        assert 0 not in nx
        # associated edges should be removed too
        assert (0,9) not in nx

    with subtests.test('Test del Edge'):
        assert (1,8) in nx
        del nx[1,8]
        assert (1,8) not in nx
        # associated nodes remain
        assert 1 in nx
        assert 8 in nx
