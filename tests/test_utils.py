from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

import pytest

from pygraph.pygraph import (
    Network,
    _deprox,  # type: ignore  # noqa: PLC2701
)
from pygraph.utils import (
    get_neighborhood,
    kevin_bacon,
    shortest_paths,
    style_edges,
    style_nodes,
)
from pygraph.vis import DefaultNetworkOptions


def test_deprox():
    """Test that nested MappingProxies are properly deproxied"""
    def assert_no_proxy(d: Mapping[Any, Any]):
        for _, v in d.items():
            assert not isinstance(v, MappingProxyType)
            if issubclass(type(v), Mapping):
                assert_no_proxy(v)
    assert_no_proxy(_deprox(DefaultNetworkOptions))
    with pytest.raises(AssertionError):
        assert_no_proxy(DefaultNetworkOptions)


def test_shortest_paths():
    """Test that all shortest paths are discovered and contain Network edges"""
    nx = Network(range(10), [
        (1, 2), (2, 4),  # P1 (2 edges)
        (1, 3), (3, 4),  # P2 (2 edges)
    ])
    paths = shortest_paths(nx, 1, 4, directed=False)
    assert len(paths) == 2, paths

    # Check that both paths are found and are not the same
    p1 = [nx[1, 2], nx[2, 4]]
    p2 = [nx[1, 3], nx[3, 4]]
    assert paths[0] == p1 or paths[0] == p2
    assert paths[1] == p1 or paths[1] == p2
    assert paths[0] != paths[1]


def test_neighborhood(subtests: pytest.Subtests):
    """Test that neighborhoods behave properly with copy flag"""
    # Create linear graph with one neigbor added per level
    nx = Network(range(10), [
        (1, 2), (2, 3), (3, 4), (4, 5),
        (5, 6), (6, 7), (7, 8), (8, 9),
    ])

    for n in range(5):
        ref_hood = get_neighborhood(nx, 1, n)
        copy_hood = get_neighborhood(nx, 1, n, copy=True)

        with subtests.test(f'Test Neighborhood Size (level:{n})'):
            assert len(ref_hood.node_map.keys()) == n + 1
            assert len(copy_hood.node_map.keys()) == n + 1

        with subtests.test(f'Test Neighborhood Nodes (level:{n})'):
            assert ref_hood.node_map == copy_hood.node_map

        with subtests.test(f'Test Copy Neighborhood References (level:{n})'):
            for n in copy_hood.node_map:
                assert nx[n] is not copy_hood[n], (id(nx[n]), id(copy_hood[n]))
            assert set(copy_hood.node_map).issubset(nx.node_map)

        with subtests.test(f'Test Reference Neighborhood Identity (level:{n})'):
            for n in ref_hood.node_map:
                assert nx[n] is ref_hood[n], (id(nx[n]), id(ref_hood[n]))
            assert set(ref_hood.node_map).issubset(nx.node_map)


def test_style_edges(subtests: pytest.Subtests):
    """Test that Edge styling works"""
    nx = Network(range(10), [(1, 2), (1, 3), (1, 4)])

    with subtests.test('Apply Edge Style'):
        style_edges(nx.edges, color={'color': 'UPDATED'})
        assert all(
            edge.data.get('color') == {'color': 'UPDATED'}
            for edge in nx.edges
        )

    with subtests.test('Reset Edge Style'):
        style_edges(nx.edges, color={})
        assert not any(
            edge.data.get('color') == {'color': 'UPDATED'}
            for edge in nx.edges
        )


def test_style_nodes(subtests: pytest.Subtests):
    """Test that Node styling works"""
    nx = Network(range(10))
    with subtests.test('Apply Node Style'):
        style_nodes(nx.nodes, color={'color': 'UPDATED'})
        assert all(
            node.data.get('color') == {'color': 'UPDATED'}
            for node in nx.nodes
        )

    with subtests.test('Reset Node Style'):
        style_nodes(nx.nodes, color={})
        assert not any(
            node.data.get('color') == {'color': 'UPDATED'}
            for node in nx.nodes
        )


# NOTE: copy flag is not tested here because
#       it is covered in the get_neigborhood tests
def test_kevin_bacon(subtests: pytest.Subtests):
    """Test that the 7-degrees neighborhood works"""
    nx = Network(range(10), [
        # 0 -> 8 are not Kevin Bacon,
        # but are with all other nodes
        (0, 1), (1, 2), (2, 3), (3, 4),
        (4, 5), (5, 6), (6, 7), (7, 8),
        # 9 is not Kevin Bacon with any node
        # (9,...)
    ])

    assert 3 in kevin_bacon(nx, 0)

    with subtests.test('Test leftmost'):
        zero = kevin_bacon(nx, 0)
        assert len(zero.node_map.keys()) == 8
        assert 8 not in zero

    with subtests.test('Test rightmost'):
        eight = kevin_bacon(nx, 8)
        assert len(eight.node_map.keys()) == 8
        assert 0 not in eight

    with subtests.test('Test orphan'):
        nine = kevin_bacon(nx, 9)
        assert len(nine.node_map.keys()) == 1
        assert 9 in nine


@pytest.mark.skip
def test_to_html():
    """Test that the network is properly rendered as html"""
    # TODO (need deterministic templates)
