import fnmatch
import hashlib
import subprocess  # noqa: S404
import tempfile
from collections.abc import (
    Iterable,
    Mapping,
)
from copy import deepcopy
from functools import cached_property
from pathlib import Path
from typing import (
    Any,
    Literal,
    Protocol,
    TypedDict,
    Unpack,
    runtime_checkable,
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
from pygraph.vis.node import Color, Icon


@runtime_checkable
class Builder(Protocol):
    """Protocol that all Builder classes need to implement"""

    def __init__(self) -> None:
        self.network_options: NetworkOptions

    @cached_property
    def data(self) -> tuple[list[Node], list[Edge]]: ...
    def reset(self) -> None: ...
    @property
    def nodes(self) -> list[Node]: ...
    @property
    def edges(self) -> list[Edge]: ...
    def network(self, *args: Any, **kwargs: Any) -> Network: ...


def _get_git(url: str) -> Path:
    repo = f'{url.rsplit('/', maxsplit=1)[-1].replace('.git', '')}'
    tmp = tempfile.TemporaryDirectory(prefix=f'{repo}_', delete=False)
    subprocess.run(['git', 'clone', url, tmp.name])
    return Path(tmp.name)


class _ExcludeOpts(TypedDict, total=False):
    files: list[Path | str]
    patterns: list[str]


class DirectoryBuilder:
    """Build a Network from a Directory"""

    def __init__(
        self,
        root: Path | str,
        *,
        file_colors: dict[str, Color | str] | None = None,
        file_icons: dict[str, Icon] | None = None,
        edge_options: EdgeOptions | None = None,
        file_node_options: NodeOptions | None = None,
        dir_node_options: NodeOptions | None = None,
        root_node_options: NodeOptions | None = None,
        network_options: NetworkOptions | None = None,
        file_node_size: Literal['filesize', 'linecount'] | None = None,
        dir_node_size: Literal['filesize', 'filecount'] | None = None,
        ignores: Path | str | list[str | Path] | _ExcludeOpts | None = None,
        verbose: bool = False,
    ) -> None:
        """..."""

        # Parse github URL or Filepath
        self.repo = None
        self.username = None
        if isinstance(root, str) and root.startswith('http'):
            parts = root.rsplit('/', maxsplit=2)
            self.repo = parts[-1].replace('.git', '')
            self.username = parts[-2]
            root = _get_git(root)
        else:
            self.repo = self.root.name
        self.root = Path(root).resolve()

        # Default options
        self.file_colors = file_colors or {}
        self.file_icons = file_icons or {}
        self.network_options = network_options or {'edges': {'arrows': 'to', 'color': {'inherit': 'to'}}}
        self.edge_options = edge_options or {}
        self.dir_node_options = dir_node_options or {'shape': 'dot'}
        self.file_node_options = file_node_options or {'shape': 'square'}
        self.root_node_options = root_node_options or {'shape': 'star'}
        self.file_node_size = file_node_size
        self.dir_node_size = dir_node_size

        # Parse ignores
        self.ignores = set(self._parse_ignores(ignores))
        self.verbose = verbose
        self.network_options['groups'] = {'useDefaultGroups': False}

        # Create style groups
        self.network_options['groups']['directory'] = self.dir_node_options
        self.network_options['groups']['file'] = self.file_node_options
        self.all_groups: dict[str, Any] = {}
        for file_extension, icon in self.file_icons.items():
            opts = deepcopy(self.file_node_options)
            color = icon.get('color', self.file_colors.get(file_extension, self._file_color(file_extension)))
            color = color.get('background', '#ffffff') if not isinstance(color, str) else color
            icon['color'] = color
            opts.update({'shape': 'icon', 'icon': icon})
            self.all_groups[file_extension] = opts

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
        d_opts: NodeOptions = {}
        d_opts.update({'label': dir.name})
        if self.dir_node_options:
            d_opts.update({'group': 'directory'})
        if self.dir_node_size is not None:
            d_opts['size'] = self._size(dir)
        return (
            Node(str(dir_stat.st_ino), **d_opts),
            Edge(str(parent_stat.st_ino), str(dir_stat.st_ino), **self.edge_options)
        )

    def _file_parts(self, fl: Path) -> tuple[Node, Edge] | None:
        fl_stat = fl.stat()
        f_opts: NodeOptions = {'label': fl.name, 'title': f'{fl.as_uri()}'}
        file_extension = fl.suffix or 'file'

        if file_extension not in self.network_options.get('groups', {}):
            groups = self.network_options.setdefault('groups', {'useDefaultGroups': False})
            if (opts := self.all_groups.get(file_extension)) is None:
                opts = deepcopy(self.file_node_options)
                opts.update({'color': self._file_color(file_extension)})
            groups[file_extension] = opts

        f_opts.update({'group': file_extension})
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
        nx[root_id].set(**self.root_node_options)
        nx[root_id].data['level'] = 0
        return nx

    def refresh(self) -> None:
        try:
            del self.data
        except AttributeError:
            pass


class GithubBuilder(DirectoryBuilder):
    def network(  # type: ignore (additional args needed)
        self,
        username: str | None = None,
        repo: str | None = None,
        branch: str = 'main',
        **options: Unpack[NetworkOptions],
    ) -> Network:
        nw = super().network(**options)
        repo = repo or self.repo
        username = username or self.username
        for node in nw.nodes:
            if 'title' in node.data:
                pth = Path(node.data['title'].replace('file:///', '')).resolve()
                if pth == self.root:
                    node.data['title'] = f'https://github.com/{username}/{repo}'
                    node.data['label'] = str(repo)
                else:
                    rel = pth.relative_to(self.root, walk_up=True).as_posix()
                    node.data['title'] = f'https://github.com/{username}/{repo}/tree/{branch}/{rel}'
        return nw
