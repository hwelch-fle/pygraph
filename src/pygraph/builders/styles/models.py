"""TypedDict models for all style submodules"""

from pathlib import Path
from typing import Literal, TypedDict

from pygraph.vis.edge import EdgeOptions
from pygraph.vis.network import NetworkOptions
from pygraph.vis.node import NodeOptions

__all__ = 'DirectoryBuilderOpts',


class _ExcludeOpts(TypedDict, total=False):
    files: list[Path | str]
    patterns: list[str]


class DirectoryBuilderOpts(TypedDict, total=False):
    file_options: NodeOptions
    dir_options: NodeOptions
    root_options: NodeOptions
    edge_options: EdgeOptions
    network_options: NetworkOptions
    file_groups: dict[str, NodeOptions]
    file_node_size: Literal['filesize', 'linecount', None]
    dir_node_size: Literal['filesize', 'filecount', None]
    ignores: Path | str | list[str | Path] | _ExcludeOpts
