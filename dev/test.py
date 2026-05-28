import webbrowser
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from pygraph.builders import GithubBuilder

env = Environment(loader=PackageLoader('pygraph'), autoescape=select_autoescape())
builder = GithubBuilder(
    r'https://github.com/hwelch-fle/pygraph.git',
    ignores={'files': ['.gitignore'], 'patterns': ['.git/', 'docs/']},
    dir_node_options={
        'shape': 'icon',
        'icon': {'code': '\uf07b'},
    },
    root_node_options={
        'icon': {
            'code': '\uf07b',
            'color': 'gold',
            'face': 'FontAwesome',
            'size': 100,
        },
        'x': 0,
        'y': 0,
        'fixed': True
    },
    file_node_options={
        'shape': 'icon',
        'icon': {'code': '\uf1c9'},
        'font': {'color': 'white'},
    },
    file_colors={
        '.js': 'green',
        '.ts': 'blue',
        '.py': 'yellow',
        '.gitignore': 'slategrey',
        '.lock': 'red',
        '.html': 'orange',
        '.md': 'purple',
    },

    # Font Awesome
    file_icons={
        '.js': {'code': '\uf3b9'},
        '.ts': {'code': '\ue840'},
        '.py': {'code': '\uf3e2'},
        '.lock': {'code': '\uf023'},
        '.html': {'code': '\uf13b'},
        '.md': {'code': '\uf60f'},
        '.rs': {'code': '\ue07a'},
        '.css': {'code': '\ue6a2'},
        '.c': {'code': '43'},
        '.cpp': {'code': '43'},
        '.zip': {'code': '\uf1c6'},
        '.php': {'code': '\uf457'},
        '.dockerfile': {'code': '\uf395'},
        '.go': {'code': '\uf395'},
        '.jinja': {'code': '\uf504'},
        '.java': {'code': '\uf4e4'},
        '.wiki': {'code': '\uf266'},
        '.sql': {'code': '\uf1c0'},
        '.r': {'code': '\uf4f7'},
        '.rb': {'code': '\uf3a5'},
        '.svg': {'code': '\uf55b'},
        '.sh': {'code': '\uf120'},
        '.bash': {'code': '\uf120'},
        '.tex': {'code': '\ue7ff'},
        '.latex': {'code': '\ue7ff'},
        '.pdf': {'code': '\uf1c1'},
        '.vue': {'code': '\uf41f'},
        '.rss': {'code': '\uf143'},
        '.png': {'code': '\uf03e'},
        '.jpg': {'code': '\uf03e'},
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
nw = builder.network(branch='master')
print(nw)
data = nw.to_dict()
out = Path(builder.root / 'out.html')
out.write_text(env.get_template('html/basic-template.html').render(
    data=data,
    pygraph={},
    jinja={'background': '#1f1f1f'},
))
webbrowser.open(str(out.resolve()))
