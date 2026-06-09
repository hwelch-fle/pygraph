from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    TypedDict,
)

from .configuration import (
    Configuration,
    DefaultConfiguration,
)
from .edge import (
    DefaultEdgeOptions,
    EdgeOptions,
)
from .group import (
    DefaultGroupOptions,
    GroupOptions,
)
from .interaction import (
    DefaultInteractionOptions,
    InteractionOptions,
)
from .layout import (
    DefaultLayoutOptions,
    LayoutOptions,
)
from .manipulation import (
    DefaultManipulationOptions,
    ManipulationOptions,
)
from .node import (
    DefaultNodeOptions,
    NodeOptions,
)
from .physics import (
    DefaultPhysicsOptions,
    PhysicsOptions,
)

__all__ = 'DefaultNetworkOptions', 'NetworkOptions'


if TYPE_CHECKING:

    class Locales(TypedDict, extra_items=dict[str, str]): ...
else:

    class Locales(TypedDict): ...


class NetworkOptions(TypedDict, total=False):
    autoResize: bool
    width: str
    height: str
    locale: str
    locales: Locales
    clickToUse: bool
    configure: Configuration
    edges: EdgeOptions
    nodes: NodeOptions
    groups: GroupOptions
    layout: LayoutOptions
    interaction: InteractionOptions
    manipulation: ManipulationOptions
    physics: PhysicsOptions


DefaultNetworkOptions: NetworkOptions = {
    'autoResize': True,
    'width': '100%',
    'height': '100%',
    'locale': 'en',
    'locales': {},
    'clickToUse': False,
    'configure': DefaultConfiguration,
    'edges': DefaultEdgeOptions,
    'nodes': DefaultNodeOptions,
    'groups': DefaultGroupOptions,
    'layout': DefaultLayoutOptions,
    'interaction': DefaultInteractionOptions,
    'manipulation': DefaultManipulationOptions,
    'physics': DefaultPhysicsOptions,
}
DefaultNetworkOptions = MappingProxyType(DefaultNetworkOptions)  # type: ignore
