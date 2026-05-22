from src.pygraph import Edge
import pytest

def test_edge_init():
    e = Edge(0,0, color='red')
    assert 'color' in e.data
    assert e.data['color'] == 'red'
    assert 'arrows' not in e.data
    assert e.key == (0,0)
    
    with pytest.raises(TypeError):
        e = Edge(1,2,4) # type: ignore
    
    e = Edge(1,2, id='Edge_ID')
    assert e['id'] == 'Edge_ID'


def test_edge_set():
    e = Edge(0,0)
    e.set(color='red', label="I'm Red", arrows='to;from')
    assert 'color' in e.data
    assert e.data['color'] == 'red'
    assert 'label' in e.data
    assert e.data['label'] == "I'm Red"
    assert 'arrows' in e.data
    assert e.data['arrows'] == 'to;from'


def test_edge_getitem():
    e = Edge(0,0, color='red', arrows='to;from')
    assert e['color'] == 'red'
    assert e['arrows'] == 'to;from'
    

def test_edge_setitem():
    e = Edge(0,0, color='red', arrows='to;from')
    e['color'] = 'blue'
    assert e.data.get('color') == 'blue'
