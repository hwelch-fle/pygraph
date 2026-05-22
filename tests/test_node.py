from src.pygraph import Node
import pytest


def test_node_init():
    n = Node(0, color='red')
    assert 'color' in n.data
    assert n.data['color'] == 'red'
    assert 'shape' not in n.data
    assert n.key == 0
    
    with pytest.raises(TypeError):
        n = Node(1,2) # type: ignore
    
    n = Node(1, label='Test')
    assert n['label'] == 'Test'


def test_node_set():
    n = Node(0)
    n.set(color='red', label="I'm Red", shape='database')
    assert 'color' in n.data
    assert n.data['color'] == 'red'
    assert 'label' in n.data
    assert n.data['label'] == "I'm Red"
    assert 'shape' in n.data
    assert n.data['shape'] == 'database'


def test_node_getitem():
    n = Node(0, color='red', shape='database')
    assert n['color'] == 'red'
    assert n['shape'] == 'database'
    

def test_node_setitem():
    n = Node(0, color='red', shape='database')
    n['color'] = 'blue'
    assert n.data.get('color') == 'blue'
