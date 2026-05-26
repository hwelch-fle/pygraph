from types import MappingProxyType
from typing import (
    Literal,
    TypedDict,
)

__all__ = 'DefaultLayoutOptions', 'LayoutOptions'


class HierarchicalLayout(TypedDict, total=False):
    enabled: bool
    levelSeparation: int
    nodeSpacing: int
    treeSpacing: int
    blockShifting: bool
    edgeMinimization: bool
    parentCentralization: bool
    direction: Literal['UD', 'DU', 'LR', 'RL']
    sortMethod: Literal['hubsize', 'directed']
    shakeTowards: Literal['leaves', 'roots']

DefaultHierarchicalLayout: HierarchicalLayout = {
    'enabled': False,
    'levelSeparation': 150,
    'nodeSpacing': 100,
    'treeSpacing': 200,
    'blockShifting': True,
    'edgeMinimization': True,
    'parentCentralization': True,
    'direction': 'UD',
    'sortMethod': 'hubsize',
}
DefaultHierarchicalLayout = MappingProxyType(DefaultHierarchicalLayout) # type: ignore


class LayoutOptions(TypedDict, total=False):
    randomSeed: int | str
    improvedLayout: bool
    clusterThreshold: int
    hierarchical: HierarchicalLayout | bool

DefaultLayoutOptions: LayoutOptions = {
    'improvedLayout': True,
    'clusterThreshold': 150,
    'hierarchical': DefaultHierarchicalLayout,
}
DefaultLayoutOptions = MappingProxyType(DefaultLayoutOptions) # type: ignore
