from types import MappingProxyType
from typing import TypedDict, TYPE_CHECKING

from .configuration import Configuration, DefaultConfiguration
from .edge import EdgeOptions, DefaultEdgeOptions, EdgeRecord as EdgeRecord
from .group import GroupOptions, DefaultGroupOptions
from .interaction import InteractionOptions, DefaultInteractionOptions
from .layout import LayoutOptions, DefaultLayoutOptions
from .manipulation import ManipulationOptions, DefaultManipulationOptions
from .node import NodeOptions, DefaultNodeOptions, NodeRecord as NodeRecord
from .physics import PhysicsOptions, DefaultPhysicsOptions


__all__ = 'NetworkOptions', 'DefaultNetworkOptions'


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
DefaultNetworkOptions = MappingProxyType(DefaultNetworkOptions) # type: ignore