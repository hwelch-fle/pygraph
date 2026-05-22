# pygraph
A wrapper for `rustworkx` that allows you to build `visjs` graphs using Python

## Getting Started
PyPi package coming soon
```
git clone https://github.com/hwelch-fle/pygraph.git
cd pygraph
pip install .
```

## Usage
More detailed Usage coming soon
```python
>>> from pygraph import Network, set
>>> nx = Network(range(10))
>>> nx.add_edges_from((i,j) if i in range(10) for j in range(10))
>>> nx
Network(N=|10|, E=|100|)
>>> 10 in nx
False
>>> 9 in nx
True
>>> (0,0) in nx
True
>>> nx[0]
Node(0, options=['label'])
>>> nx[0].data['label']
"0"
>>> nx[0].data['label'] = 'Node Zero'
>>> nx[0]
"0"
>>> nx[0].data['label']
"Node Zero"
>>> nx.get_data()
{
    'nodes': "[{'id': 0, 'label': 'Node Zero', ...}, ...], 
    'edges': "[{'from': 0, to: 0, ...}, ...]",
    'options': "{'physics': {'enabled': true}, ....}"
}
# Use this to populate HTML Jinja Template with packaged visjs
```

## Templates
Coming Soon (Currently ships with `piyvis` templates, but any `jinja2` template that uses `visjs` will work)