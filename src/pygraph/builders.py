import fnmatch
import hashlib
from collections.abc import (
    Iterable,
    Mapping,
)
from copy import deepcopy
from functools import cached_property
from pathlib import Path
from typing import (
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
    def network(self, **options: Unpack[NetworkOptions]) -> Network: ...


class _ExcludeOpts(TypedDict, total=False):
    files: list[Path | str]
    patterns: list[str]


class DirectoryBuilder:
    """Build a Network from a Directory"""

    def __init__(
        self,
        root: Path | str,
        *,
        file_colors: dict[str, str] | None = None,
        edge_options: EdgeOptions | None = None,
        file_node_options: NodeOptions | None = None,
        dir_node_options: NodeOptions | None = None,
        network_options: NetworkOptions | None = None,
        file_node_size: Literal['filesize', 'linecount'] | None = None,
        dir_node_size: Literal['filesize', 'filecount'] | None = None,
        ignores: Path | str | list[str | Path] | _ExcludeOpts | None = None,
        verbose: bool = False,
    ) -> None:
        """..."""
        self.root = Path(root)
        self.file_colors = file_colors or {}
        self.network_options = network_options or {'edges': {'arrows': 'to', 'color': {'inherit': 'from'}}}
        self.edge_options = edge_options or {}
        self.dir_node_options = dir_node_options or {'shape': 'database'}
        self.file_node_options = file_node_options or {'shape': 'box'}
        self.file_node_size = file_node_size
        self.dir_node_size = dir_node_size
        self.ignores = set(self._parse_ignores(ignores))
        self.verbose = verbose

    def _read_ignore_file(self, ig: Path) -> list[str]:
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
                    match_strings.extend(self._parse_ignores(fl))
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

    def _file_color(self, fl: Path) -> str:
        if not fl.is_file():
            return ''
        fl_typ = '.'.join(fl.suffixes)
        return (
            self.file_colors.get(fl_typ) or
            f'#{hashlib.md5(fl_typ.encode('utf-8')).hexdigest()[:6]}'  # noqa: S324
        )

    def _ignore(self, fl: Path) -> bool:
        posix = fl.as_posix()
        return (
            any(fnmatch.fnmatch(posix, ig) for ig in self.ignores)
            or any(fnmatch.fnmatch(f'{posix}/', ig) for ig in self.ignores)
        )

    def _dir_parts(self, dir: Path) -> tuple[Node, Edge] | None:
        dir_stat = dir.stat()
        parent_stat = dir.parent.stat()
        d_opts = deepcopy(self.dir_node_options)
        d_opts.update({'label': dir.name})
        if self.dir_node_size is not None:
            d_opts['size'] = self._size(dir)
        return (
            Node(dir_stat.st_ino, **d_opts),
            Edge(parent_stat.st_ino, dir_stat.st_ino, **self.edge_options)
        )

    def _file_parts(self, fl: Path) -> tuple[Node, Edge] | None:
        fl_stat = fl.stat()
        f_opts = deepcopy(self.file_node_options)
        fl_clr = self._file_color(fl)
        f_opts.update({'color': fl_clr, 'label': fl.name})
        if self.file_node_size is not None:
            f_opts['size'] = self._size(fl)
        return (
            Node(fl_stat.st_ino, **f_opts),
            Edge(fl.parent.stat().st_ino, fl_stat.st_ino, **self.edge_options),
        )

    def _walk(self) -> Iterable[tuple[Node, Edge]]:
        self.refresh()
        for root, _, files in self.root.walk(top_down=False):
            root = root.resolve()
            if self._ignore(root):
                continue
            res = self._dir_parts(root)
            if res:
                yield res
            for fl in files:
                fl = (root / fl).resolve()
                if self._ignore(fl):
                    continue
                res = self._file_parts(fl)
                if res:
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
        opts = deepcopy(self.network_options)
        opts.update(options)
        nx = Network(**opts)
        nodes = deepcopy(self.nodes)
        edges = deepcopy(self.edges)
        nx.add_nodes_from(nodes)
        nx.add_edges_from(edges)
        nx[self.root.stat().st_ino].data.update({'shape': 'star'})
        return nx

    def refresh(self) -> None:
        try:
            del self.data
        except AttributeError:
            pass
