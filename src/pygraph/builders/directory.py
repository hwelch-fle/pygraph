import fnmatch
import hashlib
import subprocess
import sys
import tempfile
from collections.abc import (
    Iterable,
    Mapping,
    MutableMapping,
)
from copy import deepcopy
from functools import cached_property
from pathlib import Path
from typing import (
    TYPE_CHECKING,
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
from pygraph.pygraph import deprox

if TYPE_CHECKING:
    from .styles.models import DirectoryBuilderOpts
else:
    DirectoryBuilderOpts = object

from pygraph.vis import (
    EdgeOptions,
    NetworkOptions,
    NodeOptions,
)

__all__ = 'DirectoryBuilder',


def _get_git(url: str) -> Path:
    repo = f'{url.rsplit('/', maxsplit=1)[-1].replace('.git', '')}'
    tmp = tempfile.TemporaryDirectory(prefix=f'{repo}_', delete=False)
    subprocess.run(['git', 'clone', '--single-branch', '--depth=1', url, tmp.name])
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


def deep_update[K, V](target: Mapping[K, V], updates: Mapping[K, V]) -> MutableMapping[K, V]:
    updated = deprox(target)
    for k in target.keys() | updates.keys():
        if k not in updates:
            continue
        if k not in target:
            updated[k] = updates[k]  # type: ignore
        elif isinstance(target[k], Mapping):
            updated[k] = deep_update(updates[k], target[k])  # type: ignore
        else:
            updated[k] = deepcopy(target[k])  # type: ignore
    return updated  # type: ignore


class DirectoryBuilder:
    """Build a Network from a Directory"""

    _trees: ClassVar[dict[str, str]] = {
        'github.com': 'tree',
        'codeberg.org': 'src',
    }

    def __init__(
        self,
        root: Path | str,
        sub_path: Path | str = '',
        style: DirectoryBuilderOpts | None = None,  # type: ignore
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
        max_size: int | None = 500,
        min_size: int | None = 50,
        directories_only: bool | None = None,
        max_levels: int | None = None,
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
        self.sub_path = root / sub_path

        # Resolve base style with overrides
        self.style: DirectoryBuilderOpts = deep_update(
            style or {},
            {
                'file_options': file_options or {},
                'dir_options': dir_options or {},
                'root_options': root_options or {},
                'edge_options': edge_options or {},
                'network_options': network_options or {},
                'file_groups': file_groups or {},
                'file_node_size': file_node_size,
                'dir_node_size': dir_node_size,
                'ignores': ignores or {},
            }
        )  # type: ignore
        self.file_options = self.style.get('file_options', {})
        self.dir_options = self.style.get('dir_options', {})
        self.root_options = self.style.get('root_options', {})
        self.edge_options = self.style.get('edge_options', {})
        self.network_options = self.style.get('network_options', {})
        self.file_groups = {ext: self._populate_group(ext, opts) for ext, opts in self.style.get('file_groups', {}).items()}
        self.file_node_size = self.style.get('file_node_size')
        self.dir_node_size = self.style.get('dir_node_size')
        self.max_size = max_size or self.style.get('max_size', sys.maxsize)
        self.min_size = min_size or self.style.get('min_size', 1)
        self.directories_only = directories_only or self.style.get('directories_only', False)
        self.max_levels = max_levels or self.style.get('max_levels', None)

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

    def _populate_group(self, file_extension: str, opts: NodeOptions) -> NodeOptions:
        temp = deepcopy(self.file_options)
        temp.pop('color', None)  # colors are set based on extension md5 hash
        if 'icon' in temp and 'color' in temp['icon']:
            temp['icon'].pop('color', None)
        temp = deep_update(temp, opts)
        opts = deep_update(opts, temp)  # type: ignore

        # If no color is set, get a unique color
        if opts.get('shape') != 'icon':
            opts.setdefault('color', self._file_color(file_extension))

        # If an icon is set, make sure the shape type is set to icon
        # Also make sure that the icon gets a unique color
        if opts.get('shape') == 'icon' and (icon := opts.get('icon')):
            icon.setdefault('color', self._file_color(file_extension))
        return opts

    def _read_ignore_file(self, ig: Path) -> list[str]:
        if not ig.is_absolute():
            ig = (self.root / ig).resolve()
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
                try:
                    with pth.open('rt', newline='\n') as lns:
                        return sum(1 for _ in lns)
                except UnicodeDecodeError:
                    return pth.stat().st_size
        return 0

    def _file_color(self, file_extension: str) -> str:
        return f'#{hashlib.md5(file_extension.encode('utf-8'), usedforsecurity=False).hexdigest()[:6]}'

    def _ignore(self, fl: Path) -> bool:
        posix = fl.as_posix()
        return (
            any(fnmatch.fnmatch(posix, ig) for ig in self.ignores)
            or any(fnmatch.fnmatch(f'{posix}/', ig) for ig in self.ignores)
        )

    def _dir_parts(self, dir: Path) -> tuple[Node, Edge] | None:
        dir_rel = dir.relative_to(self.sub_path).as_posix()
        parent_rel = (
            dir.parent.relative_to(self.sub_path).as_posix()
            if dir.parent.is_relative_to(self.sub_path)
            else self.sub_path.relative_to(self.root).as_posix()
        )
        d_opts: NodeOptions = {
            'label': dir.name,
            'title': dir.as_posix(),
            'group': 'directory',
            'link': dir.as_uri(),
            'level': len(dir.relative_to(self.sub_path).parts)
        }
        if self.dir_node_size is not None:
            d_opts['size'] = max(self.min_size, min(self._size(dir), self.max_size))
        return (
            Node(dir_rel, **d_opts),
            Edge(parent_rel, dir_rel, **self.edge_options)
        )

    def _file_parts(self, fl: Path) -> tuple[Node, Edge] | None:
        if self._ignore(fl) or not fl.is_relative_to(self.root):
            return
        fl_rel = fl.relative_to(self.sub_path).as_posix()
        parent_rel = (
            fl.parent.relative_to(self.sub_path).as_posix()
            if fl.parent.is_relative_to(self.sub_path)
            else self.sub_path.relative_to(self.root).as_posix()
        )
        f_opts: NodeOptions = {
            'label': fl.name,
            'title': fl_rel,
            'link': fl.as_uri(),
            'group': fl.suffix or 'file',
            'level': len(fl.relative_to(self.sub_path).parts)
        }
        groups = self.network_options.setdefault('groups', {'useDefaultGroups': False})
        if (ext := f_opts['group']) not in groups:
            groups[ext] = self.file_groups.get(ext, self._populate_group(ext, deepcopy(self.file_options)))

        if self.file_node_size is not None:
            f_opts['size'] = max(self.min_size, min(self._size(fl), self.max_size))

        return (
            Node(fl_rel, **f_opts),
            Edge(parent_rel, fl_rel, **self.edge_options),
        )

    def _walk(self) -> Iterable[tuple[Node, Edge]]:
        self.refresh()
        for root, _, files in self.sub_path.walk():
            if self._ignore(root):
                continue
            if res := self._dir_parts(root.resolve()):
                yield res
            if not self.directories_only:
                for fl in files:
                    if res := self._file_parts((root / fl).resolve()):
                        yield res

    # Only use when you want to limit traversal
    def _fast_walk(self, root: Path, levels: int) -> Iterable[tuple[Node, Edge]]:
        if levels == 0:
            return
        if res := self._dir_parts(root.resolve()):
            yield res
        for child in root.iterdir():
            if child.is_dir():
                yield from self._fast_walk(child, levels - 1)
            elif not self.directories_only:
                if res := self._file_parts(child):
                    yield res

    def _create_link(self, node: Node, *, host: str, user: str, repo: str, branch: str, tree: str) -> None:
        # Skip nodes with no link set
        if 'link' not in node.data or not isinstance(node.data['link'], str):
            return

        # Path.resolve() will incorrectly resolve URIs that start with
        # file:///<DRIVE>:/... as /<DRIVE>:/... on Windows, we need to
        # check for this and strip the leading / if /<DRIVE>: is detected
        #
        # https://www.rfc-editor.org/rfc/rfc8089.html#appendix-E.2
        #
        # This issue will be resolved in upcoming versions
        # https://discuss.python.org/t/file-uris-in-python/15600/8
        link = node.data['link'].replace('file://', '')
        if sys.platform == 'win32' and (link[0], link[2]) == ('/', ':'):
            link = link[1:]

        pth = Path(link).resolve()

        # Handle Root Node
        if pth == self.sub_path:
            if (self.sub_path != self.root) and (rel := self.sub_path.relative_to(self.root)):
                node.data['link'] = f'https://{host}/{user}/{repo}/{tree}/{branch}/{rel}'
                node.data['title'] = f'{repo}/{rel}'
            else:
                node.data['link'] = f'https://{host}/{user}/{repo}'
                node.data['title'] = f'{repo}'
                node.data['label'] = f'{repo}'
            return

        # Handle all child nodes
        rel = pth.relative_to(self.root, walk_up=True).as_posix()
        node.data['link'] = f'https://{host}/{user}/{repo}/{tree}/{branch}/{rel}'

    def delete_directory(self, *, force: bool = False):
        """Delete the root directory (used when targeting a web-repo and git-cloning into a tempdir)"""
        is_temp = self.root.is_relative_to(Path(tempfile.TemporaryDirectory(delete=True).name).parent)
        if not is_temp and not force:
            raise FileExistsError(f'{self.root} is not a temp directory, run with `force = True` to force delete')
        for r, ds, fs in self.root.walk(top_down=False):
            r.chmod(0o0200)
            for f in fs:
                f = r / f
                f.chmod(0o0200)
                f.unlink()
            for d in ds:
                d = r / d
                d.rmdir()
        self.root.rmdir()

    @cached_property
    def data(self) -> tuple[list[Node], list[Edge]]:
        nodes = list[Node]()
        edges = list[Edge]()
        for nd, ed in (self._walk() if not self.max_levels else self._fast_walk(self.root, self.max_levels)):
            nodes.append(nd)
            if len(set(ed.key)) > 1:
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
        root_id = '.'
        nx[root_id].set(**self.root_options)
        nx[root_id].data['level'] = 0
        return nx

    def web_network(
        self,
        host: str | None = None,
        user: str | None = None,
        repo: str | None = None,
        branch: str | None = None,
        tree: str | None = None,
        **options: Unpack[NetworkOptions],
    ) -> Network:
        """Get a network """
        host = host or self.host
        user = user or self.user
        repo = repo or self.repo
        tree = tree or self._trees.get(str(host), 'blob')
        branch = branch or _get_branch(self.root)
        if not all((host, user, branch, tree)):
            raise ValueError(
                'web_network requires that a repo, user, and host are set '
                f'({host=}, {user=}, {repo=}, {tree=}, {branch=})'
            )
        nw = self.network(**options)
        for node in nw.nodes:
            self._create_link(
                node,
                host=str(host),
                user=str(user),
                repo=str(repo),
                branch=str(branch),
                tree=tree,
            )
        return nw

    def refresh(self) -> None:
        try:
            del self.data
        except AttributeError:
            pass
