import datetime
import json
from collections import Counter
from hashlib import md5
from itertools import pairwise
from pathlib import Path
from typing import Any, Unpack
from urllib.request import urlopen

from jinja2 import Environment, PackageLoader, select_autoescape

from pygraph.builders.styles import GitRepoStyle
from pygraph.pygraph import Edge, Network, Node
from pygraph.utils import to_html
from pygraph.vis.network import NetworkOptions

ENV = Environment(loader=PackageLoader('pygraph'), autoescape=select_autoescape())

HANDLERS: list[str] = []
HANDLERS.append(
"""on('doubleClick', function (event) {
    const node = network.body.data.nodes.get(event.nodes[0]);
    if (node && node.link) { window.open(node.link) };
});
""")


STATUS = {
    'Final': 'green',
    'Accepted': 'lawngreen',
    'Active': 'yellow',
    'Deferred': 'orange',
    'Rejected': 'red',
    'Superseded': 'hotpink',
    'Withdrawn': 'black',
    'Draft': 'slategrey',
}
TYPE = {'Informational', 'Process', 'Standards Track'}
TOPIC = {
    'governance',
    'governance, packaging',
    'governance, typing',
    'packaging',
    'packaging, typing',
    'release',
    'typing',
}


class PepBuilder:
    """Build an interactive graph of Python PEPs and their relationships"""
    def __init__(self) -> None:
        with urlopen('https://peps.python.org/api/peps.json') as response:
            self.peps: dict[str, dict[str, Any]] = json.load(response)
        self.peps = {num: pep for num, pep in self.peps.items() if pep['status'] in ('Active', 'Accepted', 'Final') and pep['number'] != 733}
        self._authors: list[tuple[str, str]] = [
            (author, f'{pep['number']}: {pep['title']}')
            for pep in self.peps.values()
            for author in pep['author_names']
        ]
        self.authored_count = Counter(a[0] for a in self._authors)
        self.authors = {a[0] for a in self._authors}
        self.authored_list = {
            author: [a[1] for a in self._authors if a[0] == author]
            for author in self.authors
        }

    def network(self, **options: Unpack[NetworkOptions]) -> Network:
        nx = Network(**options)
        nx.add_nodes_from(
            Node(
                author,
                title=author,
                label=f'{author}',
                shape='icon',
                icon={
                    'code': '\uf007',
                    'color': f'#{md5(author.encode('utf-8'), usedforsecurity=False).hexdigest()[:6]}',
                    'size': min(300, max([25, 10 * self.authored_count[author]]))
                },
                color=f'#{md5(author.encode('utf-8'), usedforsecurity=False).hexdigest()[:6]}',
            )
            for author in self.authors
        )
        # nx.add_nodes_from(
        #     Node(
        #         num,
        #         title=pep['title'],
        #         label=pep['title'],
        #         shape='icon',
        #         link=pep['url'],
        #         icon={'code': str(num).zfill(4), 'color': STATUS.get(pep['status'], 'white')}, color=STATUS.get(pep['status'], 'white'),
        #     )
        #     for num, pep in self.peps.items()
        # )
        for num, pep in self.peps.items():
            for author in pep['author_names']:
                for other_author in pep['author_names']:
                    if other_author == author and len(pep['author_names']) > 1:
                        print(f'skipping self for {author}: PEP {pep['number']}: {pep['title']}')
                        continue
                    if (other_author, author) in nx and nx[other_author, author]['title'] == f'PEP {num}: {pep['title']}':
                        continue
                    nx.add_edge(
                        Edge(
                            author, other_author,
                            title=f'PEP {num}: {pep['title']}',
                            label=f'PEP {num}: {pep['title']}',
                            arrows={'from': {'enabled': True}, 'to': {'enabled': True}},
                            color={'inherit': 'both'},
                            length=1000,
                            link=pep['url'],
                            num=pep['number'],
                            font={'align': 'middle'},
                        )
                    )
        for n in nx.nodes:
            n['icon']['size'] = max(25, min(10 * len(nx.adj_list(n)), 500))
        nx.pre_solve()
        return nx

    def _network(self, **options: Unpack[NetworkOptions]) -> Network:
        nx = Network(**options)
        nx.add_nodes_from(
            Node(
                num,
                title=pep['title'],
                label=pep['title'],
                shape='icon',
                link=pep['url'],
                icon={'code': str(num).zfill(4), 'color': STATUS.get(pep['status'], 'white')}, color=STATUS.get(pep['status'], 'white'),
            )
            for num, pep in self.peps.items()
        )
        for num, pep in self.peps.items():
            if replaces := pep['replaces']:
                for other in replaces.split(', '):
                    if other not in nx:
                        continue
                    nx.add_edge(
                        Edge(
                            num, other,
                            color={'color': 'red'},
                            length=300,
                        )
                    )

        peps = list(self.peps.values())
        peps.sort(
            key=lambda pep: datetime.datetime.strptime(pep['created'], '%d-%b-%Y').astimezone(datetime.UTC)
        )
        peps = [p for p in peps if p['status'] in ['Final', 'Accepted', 'Active']]
        for fr, to in pairwise(peps):
            nx.add_edge(
                Edge(
                    str(fr['number']), str(to['number']),
                    color={'inherit': 'to'},
                    length=300,
                )
            )
        return nx


if __name__ == '__main__':
    out = Path('pep.html')
    opts = GitRepoStyle.get('network_options', {})
    builder = PepBuilder()
    nw = builder.network(**opts)
    nw.barnes_hut(
        centralGravity=1, springConstant=0.01, gravitationalConstant=-50000, theta=0.75,
    )
    out.write_text(
        to_html(
            nw,
            ENV.get_template('html/basic-template.html'),
            jinja={'title': 'PEPs', 'filtering': {'edges_lookup': ['title']}},
            pygraph={'handlers': HANDLERS}
        )
    )
    print(nw)
