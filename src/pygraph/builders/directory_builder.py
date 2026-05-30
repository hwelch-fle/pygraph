import fnmatch
import hashlib
import subprocess
import tempfile
from collections.abc import (
    Iterable,
    Mapping,
)
from copy import deepcopy
from functools import cached_property
from pathlib import Path
from typing import (
    ClassVar,
    Literal,
    TypedDict,
    Unpack,
)

from pygraph import (
    Edge,
    Network,
    Node,
)
from pygraph.vis import (
    EdgeOptions,
    NetworkOptions,
    NodeOptions,
)

__all__ = 'DirectoryBuilder',


def _get_git(url: str) -> Path:
    repo = f'{url.rsplit('/', maxsplit=1)[-1].replace('.git', '')}'
    tmp = tempfile.TemporaryDirectory(prefix=f'{repo}_', delete=False)
    subprocess.run(['git', 'clone', url, tmp.name])
    return Path(tmp.name)


def _get_branch(repo: Path) -> str:
    res = subprocess.run(['git', 'branch', '--list'], cwd=repo, capture_output=True)
    for branch in res.stdout.decode('utf-8').split('\n'):
        if branch.startswith('*'):
            return branch.split()[-1]
    return 'main'


class _ExcludeOpts(TypedDict, total=False):
    files: list[Path | str]
    patterns: list[str]


class DirectoryBuilder:
    """Build a Network from a Directory"""

    _trees: ClassVar[dict[str, str]] = {
        'github.com': 'tree',
        'codeberg.org': 'src',
    }

    def __init__(
        self,
        root: Path | str,
        *,
        file_options: NodeOptions | None = None,
        dir_options: NodeOptions | None = None,
        root_options: NodeOptions | None = None,
        edge_options: EdgeOptions | None = None,
        network_options: NetworkOptions | None = None,
        file_groups: dict[str, NodeOptions] | None = None,
        file_node_size: Literal['filesize', 'linecount'] | None = None,
        dir_node_size: Literal['filesize', 'filecount'] | None = None,
        ignores: Path | str | list[str | Path] | _ExcludeOpts | None = None,
    ) -> None:
        """..."""

        # Parse github URL or Filepath
        if isinstance(root, str) and root.startswith('http'):
            host, user, repo, root = self._clone_repo(root)
        else:
            root = Path(root).resolve()
            host, user, repo, root = (None, None, root.name, root)

        self.host = host
        self.user = user
        self.repo = repo
        self.root = root

        # Default options
        self.network_options = network_options or {}
        self.edge_options = edge_options or {}
        self.dir_options = dir_options or {}
        self.file_options = file_options or {}
        self.root_options = root_options or {}
        self.file_groups = self._populate_groups(file_groups or {})
        self.file_node_size = file_node_size
        self.dir_node_size = dir_node_size

        # Parse ignores
        self.ignores = set(self._parse_ignores(ignores))
        self.network_options['groups'] = {'useDefaultGroups': False}

        # Create style groups
        self.network_options['groups']['directory'] = self.dir_options
        self.network_options['groups']['file'] = self.file_options

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.repo})'

    def _clone_repo(self, url: str) -> tuple[str, str, str, Path]:
        parts = url.rsplit('/', maxsplit=3)
        return parts[-3], parts[-2], parts[-1].removesuffix('.git'), _get_git(url)

    def _populate_groups(self, groups: dict[str, NodeOptions]) -> dict[str, NodeOptions]:
        # Pull default file options and update them with file specifics
        for opts in groups.values():
            temp = deepcopy(self.file_options)
            temp.pop('color', None)  # colors are set based on extension md5 hash
            temp.update(opts)
            opts.update(temp)

        # General transformations
        for file_extension, opts in groups.items():
            groups[file_extension] = opts

            # If an icon is set, make sure the shape type is set to icon
            # Also make sure that the icon gets a unique color
            if 'icon' in opts:
                opts['shape'] = 'icon'
                if 'color' not in opts['icon']:
                    opts['icon']['color'] = self._file_color(file_extension)

            # If no color is set, get a unique color
            elif 'color' not in opts:
                opts['color'] = self._file_color(file_extension)
        return groups

    def _read_ignore_file(self, ig: Path) -> list[str]:
        if not ig.is_absolute():
            ig = self.root / ig
        if not ig.is_file() or not ig.exists():
            raise ValueError(f'Path object: {ig} does not exist or is not a file.')

        return [
            line.strip() for line in ig.read_text().split('\n')
            if line and line[0] != '#'
        ]

    def _parse_ignores(self, ignores: str | Path | list[str | Path] | _ExcludeOpts | None) -> list[str]:
        match_strings: list[str] = []

        match ignores:
            case None:
                return match_strings
            case Path():
                match_strings.extend(self._read_ignore_file(Path(ignores)))
            case str():
                match_strings.append(ignores)
            case [str() | Path()]:
                for ig in ignores:
                    match_strings.extend(self._parse_ignores(ig))
            case Mapping():
                for fl in ignores.get('files', []):
                    match_strings.extend(self._parse_ignores(Path(fl)))
                for pat in ignores.get('patterns', []):
                    match_strings.extend(self._parse_ignores(pat))
            case _:
                raise ValueError(f'invalid ignore: {ignores}')

        # Add exclude for directory contents and directory itself
        return [f'*{ms}*' for ms in match_strings]

    def _size(self, pth: Path) -> int:
        """filesize in bytes (if a dir, contained bytes)"""
        if pth.is_dir():
            if self.dir_node_size == 'filesize':
                return sum(self._size(fl) for fl in pth.iterdir())
            else:
                return sum(1 for _ in pth.iterdir())
        elif pth.is_file():
            if self.file_node_size == 'filesize':
                return pth.stat().st_size
            else:
                with pth.open('rt') as lns:
                    return sum(1 for _ in lns)
        return 0

    def _file_color(self, file_extension: str) -> str:
        return f'#{hashlib.md5(file_extension.encode('utf-8')).hexdigest()[:6]}'  # noqa: S324

    def _ignore(self, fl: Path) -> bool:
        posix = fl.as_posix()
        return (
            any(fnmatch.fnmatch(posix, ig) for ig in self.ignores)
            or any(fnmatch.fnmatch(f'{posix}/', ig) for ig in self.ignores)
        )

    def _dir_parts(self, dir: Path) -> tuple[Node, Edge] | None:
        dir_stat = dir.stat()
        parent_stat = dir.parent.stat()
        d_opts: NodeOptions = {
            'label': dir.name if dir != self.root else self.repo,
            'title': dir.relative_to(self.root).as_posix(),
            'group': 'directory',
            'link': dir.as_uri(),
        }
        if self.dir_node_size is not None:
            d_opts['size'] = self._size(dir)
        return (
            Node(str(dir_stat.st_ino), **d_opts),
            Edge(str(parent_stat.st_ino), str(dir_stat.st_ino), **self.edge_options)
        )

    def _file_parts(self, fl: Path) -> tuple[Node, Edge] | None:
        fl_stat = fl.stat()
        f_opts: NodeOptions = {
            'label': fl.name,
            'title': fl.relative_to(self.root).as_posix(),
            'link': fl.as_uri(),
            'group': fl.suffix or 'file'
        }
        if f_opts['group'] not in self.network_options.get('groups', {}):
            groups = self.network_options.setdefault('groups', {'useDefaultGroups': False})
            groups[f_opts['group']] = self.file_groups.get(f_opts['group'], self.file_options)

        if self.file_node_size is not None:
            f_opts['size'] = self._size(fl)

        return (
            Node(str(fl_stat.st_ino), **f_opts),
            Edge(str(fl.parent.stat().st_ino), str(fl_stat.st_ino), **self.edge_options),
        )

    def _walk(self) -> Iterable[tuple[Node, Edge]]:
        self.refresh()
        for root, _, files in self.root.walk(top_down=True):
            root = root.resolve()
            if self._ignore(root):
                continue
            res = self._dir_parts(root)
            if res:
                res[0].data['level'] = len(root.relative_to(self.root).parts)
                yield res
            for fl in files:
                fl = (root / fl).resolve()
                if self._ignore(fl):
                    continue
                res = self._file_parts(fl)
                if res:
                    res[0].data['level'] = len(fl.relative_to(self.root).parts)
                    yield res

    def _create_link(self, node: Node, *, host: str, user: str, branch: str, tree: str) -> None:
        # Skip nodes with no link set
        if 'link' not in node.data or not isinstance(node.data['link'], str):
            return

        pth = Path(node.data['link'].replace('file://', '')).resolve()

        # Handle Root Node
        if pth == self.root:
            node.data['link'] = f'https://{host}/{user}/{self.repo}'
            node.data['title'] = self.repo
            return

        # Handle all child nodes
        rel = pth.relative_to(self.root, walk_up=True).as_posix()
        node.data['link'] = f'https://{host}/{user}/{self.repo}/{tree}/{branch}/{rel}'

    @cached_property
    def data(self) -> tuple[list[Node], list[Edge]]:
        nodes = list[Node]()
        edges = list[Edge]()
        for nd, ed in self._walk():
            nodes.append(nd)
            edges.append(ed)
        node_ids = {n.key for n in nodes}
        edges = [e for e in edges if all(n in node_ids for n in e.key)]
        return nodes, edges

    @property
    def nodes(self) -> list[Node]:
        return self.data[0]

    @property
    def edges(self) -> list[Edge]:
        return self.data[1]

    def network(self, **options: Unpack[NetworkOptions]) -> Network:
        """Get a Network object from the builder

        Args:
            **options: Any additional options you want to set at the Network level

        Note:
            When called, the Node/Edge data from the Builder is deepcopied into the Network.
        """
        nodes = deepcopy(self.nodes)
        edges = deepcopy(self.edges)
        opts = deepcopy(self.network_options)
        opts.update(options)
        nx = Network(**opts)
        nx.add_nodes_from(nodes)
        nx.add_edges_from(edges)
        root_id = str(self.root.stat().st_ino)
        nx[root_id].set(**self.root_options)
        nx[root_id].data['level'] = 0
        return nx

    def web_network(
        self,
        host: str | None = None,
        user: str | None = None,
        branch: str | None = None,
        tree: str | None = None,
        **options: Unpack[NetworkOptions],
    ) -> Network:
        """Get a network """
        host = host or self.host
        user = user or self.user
        tree = tree or self._trees.get(str(self.host), 'blob')
        branch = branch or _get_branch(self.root)
        if not host and user and branch and tree:
            raise ValueError(
                'web_network requires that a repo host and username are set '
                f'({host=}, {user=}, {tree=}, {branch=})'
            )
        nw = self.network(**options)
        for node in nw.nodes:
            self._create_link(
                node, host=str(host), user=str(user), branch=str(branch), tree=tree
            )
        return nw

    def refresh(self) -> None:
        try:
            del self.data
        except AttributeError:
            pass
