import webbrowser
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from pygraph.builders.directory_builder import DirectoryBuilder
from pygraph.utils import to_html

env = Environment(loader=PackageLoader('pygraph'), autoescape=select_autoescape())
builder = DirectoryBuilder(
    r'https://github.com/plankanban/planka.git',
    ignores={'files': ['.gitignore'], 'patterns': ['.git/']},
    dir_options={
        'shape': 'icon',
        'icon': {'code': '\uf07b'},
    },
    root_options={
        'icon': {'code': '\uf07b', 'color': 'gold', 'size': 100},
        'x': 0,
        'y': 0,
        'fixed': True
    },
    file_options={
        'shape': 'icon',
        'icon': {'code': '\uf1c9', 'color': '#3572a5'},
        'font': {'color': 'white', 'strokeWidth': 3},
    },

    # Font Awesome
    file_groups={
        '.js': {
            'shape': 'icon',
            'icon': {'code': '\uf3b9', 'color': 'green'}
        },
        '.ts': {
            'shape': 'icon',
            'icon': {'code': '\ue840', 'color': 'blue'}
        },
        '.py': {
            'shape': 'icon',
            'icon': {'code': '\uf3e2', 'color': 'yellow'}
        },
        '.lock': {
            'shape': 'icon',
            'icon': {'code': '\uf023', 'color': 'red'}
        },
        '.html': {
            'shape': 'icon',
            'icon': {'code': '\uf13b', 'color': 'orange'}
        },
        '.md': {
            'shape': 'icon',
            'icon': {'code': '\uf60f', 'color': 'purple'}
        },
        '.rs': {
            'shape': 'icon',
            'icon': {'code': '\ue07a'}
        },
        '.css': {
            'shape': 'icon',
            'icon': {'code': '\ue6a2'}
        },
        '.c': {
            'shape': 'icon',
            'icon': {'code': '43'}
        },
        '.cpp': {
            'shape': 'icon',
            'icon': {'code': '43'}
        },
        '.zip': {
            'shape': 'icon',
            'icon': {'code': '\uf1c6'}
        },
        '.php': {
            'shape': 'icon',
            'icon': {'code': '\uf457'}
        },
        '.dockerfile': {
            'shape': 'icon',
            'icon': {'code': '\uf395'}
        },
        '.go': {
            'shape': 'icon',
            'icon': {'code': '\uf395'}
        },
        '.jinja': {
            'shape': 'icon',
            'icon': {'code': '\uf504'}
        },
        '.java': {
            'shape': 'icon',
            'icon': {'code': '\uf4e4'}
        },
        '.wiki': {
            'shape': 'icon',
            'icon': {'code': '\uf266'}
        },
        '.sql': {
            'shape': 'icon',
            'icon': {'code': '\uf1c0'}
        },
        '.r': {
            'shape': 'icon',
            'icon': {'code': '\uf4f7'}
        },
        '.rb': {
            'shape': 'icon',
            'icon': {'code': '\uf3a5'}
        },
        '.svg': {
            'shape': 'icon',
            'icon': {'code': '\uf55b'}
        },
        '.sh': {
            'shape': 'icon',
            'icon': {'code': '\uf120'}
        },
        '.bash': {
            'shape': 'icon',
            'icon': {'code': '\uf120'}
        },
        '.tex': {
            'shape': 'icon',
            'icon': {'code': '\ue7ff'}
        },
        '.latex': {
            'shape': 'icon',
            'icon': {'code': '\ue7ff'}
        },
        '.pdf': {
            'shape': 'icon',
            'icon': {'code': '\uf1c1'}
        },
        '.vue': {
            'shape': 'icon',
            'icon': {'code': '\uf41f'}
        },
        '.rss': {
            'shape': 'icon',
            'icon': {'code': '\uf143'}
        },
        '.png': {
            'shape': 'icon',
            'icon': {'code': '\uf03e'}
        },
        '.jpg': {
            'shape': 'icon',
            'icon': {'code': '\uf03e'}
        },
    },
    network_options={
        'edges': {
            'arrows': 'to',
            'color': {'inherit': 'to', 'hover': 'gold'},
            'arrowStrikethrough': True,
            'endPointOffset': {'to': -5},
            'width': 3,
            'hoverWidth': 5,
            'length': 50,
        },
        'nodes': {
            'shadow': {
                'color': '#454545',
                'size': 3,
                'x': 1,
                'y': 1,
            },
            'font': {
                'color': '#ffffff',
                'size': 20,
                'strokeWidth': 5,
                'strokeColor': "#4e4e4e"
            },
        },
        'interaction': {
            'selectConnectedEdges': True,
            'navigationButtons': True,
            'hoverConnectedEdges': True,
            'keyboard': {'enabled': True},
        },
        'physics': {
            'solver': 'barnesHut',
            'barnesHut': {
                'avoidOverlap': 1,
                'centralGravity': 0.1,
                'gravitationalConstant': -15000,
            },
        },
        'configure': {
            'filter': False,
        },
    },
)

nw = builder.web_network()
print(nw)

data = nw.to_dict()
out = Path(builder.root / f'{builder.repo}.html')
template = env.get_template('html/basic-template.html')
out.write_text(to_html(nw, template, jinja={'background': '#1f1f1f'}))
webbrowser.open(str(out.resolve()))
