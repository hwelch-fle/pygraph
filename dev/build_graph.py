from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import md5
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from pygraph.builders import DirectoryBuilder
from pygraph.builders.styles import GitRepoStyle
from pygraph.pygraph import Network, Node
from pygraph.utils import to_html

ENV = Environment(loader=PackageLoader('pygraph'), autoescape=select_autoescape())

TARGETS = [
    # Qiskit
    'https://github.com/Qiskit/rustworkx.git',

    # visjs
    'https://github.com/visjs/vis-network.git',

    # fastapi
    'https://github.com/fastapi/fastapi.git',
    'https://github.com/fastapi/typer.git',

    # pallets
    'https://github.com/pallets/jinja.git',
    'https://github.com/pallets/click.git',

    # encode
    'https://github.com/encode/httpx.git',

    # pytest
    'https://github.com/pytest-dev/pytest.git',

    # pytest-benchmark
    'https://github.com/ionelmc/pytest-benchmark.git',

    # python
    'https://github.com/python/cpython.git',
    'https://github.com/python/peps.git',

    # hwelch-fle
    'https://github.com/hwelch-fle/pygraph.git',
    'https://github.com/hwelch-fle/plankapy.git',
    'https://github.com/hwelch-fle/arcpie.git',
    'https://github.com/hwelch-fle/geo-grab.git',
    'https://github.com/hwelch-fle/cimple.git',
]


HANDLERS: list[str] = []
HANDLERS.append(
"""on('doubleClick', function (event) {
    const node = network.body.data.nodes.get(event.nodes[0]);
    if (node) { window.open(node.link) };
});
""")


def build_graph(url: str) -> DirectoryBuilder:
    template = ENV.get_template('html/basic-template.html')
    builder = DirectoryBuilder(
        url,
        style=GitRepoStyle,
        ignores={'patterns': ['.git/']},
        network_options={'nodes': {'font': {'face': 'JetBrains Mono'}}},
    )
    nx = builder.web_network()
    out = Path(f'docs/ref/repo-graphs/{builder.user}/{builder.repo}.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    html = to_html(
        nx,
        template,
        jinja={
            'background': '#1f1f1f',
            'font': 'JetBrains Mono',
            'title': builder.repo,
        },
        pygraph={'handlers': HANDLERS}
    )
    out.write_text(html)
    return builder


def main() -> None:
    template = ENV.get_template('html/basic-template.html')
    built: list[DirectoryBuilder] = []

    with ThreadPoolExecutor(len(TARGETS), thread_name_prefix='pygraph-') as executor:
        futs = {executor.submit(build_graph, targ): targ for targ in TARGETS}
        for future in as_completed(futs):
            try:
                builder = future.result(timeout=60)
            except TimeoutError as e:
                print(f'\n[FAILED]: {futs[future]} timed out ({e})')
                continue
            print(f'\nbuilt {builder.repo}')
            built.append(builder)

    nx = Network(
        nodes={
            'shape': 'star',
            'font': {'face': 'JetBrains Mono', 'color': '#ffffff', 'strokeColor': '#434343', 'strokeWidth': 3},
        },
        edges={
            'arrows': 'to',
            'length': 200,
        },
    )
    nx.barnes_hut(gravitationalConstant=-6000, avoidOverlap=0.75)

    for builder in built:
        repo = builder.repo
        user = str(builder.user)
        if f'user:{user}' not in nx:
            usr_clr = f'#{md5(user.encode('utf-8'), usedforsecurity=False).hexdigest()[:6]}'
            groups = nx.options.setdefault('groups', {'useDefaultGroups': False})
            assert 'groups' in nx.options
            groups[user] = {'color': usr_clr}
            user_node = Node(
                f'user:{user}',
                label=user,
                title=user,
                image=f'https://github.com/{user}.png?size=100',
                shape='circularImage',
                link=f'https://github.com/{user}',
                shapeProperties={'useBorderWithImage': True, 'borderRadius': 10},
                shadow={'color': usr_clr, 'enabled': True, 'size': 5, 'x': 3, 'y': 3},
                color="#7C7C7CAB",
            )
            nx.add_node(user_node)
        repo_node = Node(
            f'repo:{repo}',
            label=repo,
            title=repo,
            link=f'repo-graphs/{user}/{repo}.html',
            group=user,
        )
        nx.add_node(repo_node)
        nx.add_edge((f'user:{user}', f'repo:{repo}'))
        builder.delete_directory()
        print(f'cleaned up {repo}')

    out = Path('docs/ref/index.html')
    html = to_html(
        nx,
        template,
        jinja={
            'background': '#1f1f1f',
            'font': 'JetBrains Mono',
            'title': 'Home',
        },
        pygraph={'handlers': HANDLERS}
    )
    print('\nwriting index...')
    out.write_text(html)


if __name__ == '__main__':
    main()
