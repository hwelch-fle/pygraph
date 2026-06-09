"""Protocol that all Builders need to implement"""

from collections.abc import Mapping
from typing import Any, Protocol, Unpack

from pygraph import Edge, Network, Node
from pygraph.vis.network import NetworkOptions


class BuilderProto[Style: Mapping[Any, Any]](Protocol):
    def __init__(self, style: Style, *args: Any, **kwargs: Any) -> None:
        self.style: Style
        """Style object for the Builder"""
        self._data: tuple[list[Node], list[Edge]] | None
        """Data cache for the builder"""

    @property
    def data(self) -> tuple[list[Node], list[Edge]]:
        """Descriptor for accessing underlying _data cache/building the network"""
        ...

    @property
    def nodes(self) -> list[Node]:
        """Descriptor for accessing the node list"""
        ...

    @property
    def edges(self) -> list[Edge]:
        """Descriptor for accessing the edge list"""
        ...

    def network(self, **options: Unpack[NetworkOptions]) -> Network:
        """Method that generates a Network option for the Builder"""
        ...

    def refresh(self) -> None:
        """Reset the data cache"""
        ...
