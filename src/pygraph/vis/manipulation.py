from types import MappingProxyType
from typing import (
    Any,
    TypedDict,
)

from .node import NodeOptions

__all__ = 'DefaultManipulationOptions', 'ManipulationOptions'


type JSFunc = Any


class ManipulationOptions(TypedDict, total=False):
    enabled: bool
    initiallyActive: bool
    addNode: bool | JSFunc
    addEdge: bool | JSFunc
    editNode: JSFunc
    editEdge: bool | JSFunc
    deleteNode: bool | JSFunc
    deleteEdge: bool | JSFunc
    controlNodeStyle: NodeOptions


DefaultControlNode: NodeOptions = {
    'shape': 'dot',
    'size': 6,
    'color': {'background': '#ff0000', 'border': '#3c3c3c', 'highlight': {'background': '#07f968', 'border': '#3c3c3c'}},
    'borderWidth': 2,
    'borderWidthSelected': 2,
}

DefaultManipulationOptions: ManipulationOptions = {
    'enabled': False,
    'initiallyActive': True,
    'addNode': True,
    'addEdge': True,
    'editEdge': True,
    'deleteNode': True,
    'deleteEdge': True,
    'controlNodeStyle': DefaultControlNode,
}
DefaultManipulationOptions = MappingProxyType(DefaultManipulationOptions)  # type: ignore
