from typing import TypedDict
from types import MappingProxyType


__all__ = 'InteractionOptions', 'DefaultInteractionOptions'


class Speed(TypedDict, total=False):
    x: int
    y: int
    zoom: float

DefaultSpeed: Speed = {
    'x': 1,
    'y': 1,
    'zoom': 0.02,
}
DefaultSpeed = MappingProxyType(DefaultSpeed) # type: ignore

class KeyboardInteraction(TypedDict, total=False):
    enabled: bool
    speed: Speed
    bindToWindow: bool
    autoFocus: bool

DefaultKeyboardInteraction: KeyboardInteraction = {
    'enabled': False,
    'speed': DefaultSpeed,
    'bindToWindow': True,
    'autoFocus': True,
}
DefaultKeyboardInteraction = MappingProxyType(DefaultKeyboardInteraction) # type: ignore

class InteractionOptions(TypedDict, total=False):
    dragNodes: bool
    dragView: bool
    hideEdgesOnDrag: bool
    hideEdgesOnZoom: bool
    hideNodesOnDrag: bool
    hover: bool
    hoverConnectedEdges: bool
    keyboard: KeyboardInteraction
    multiselect: bool
    navigationButtons: bool
    selectable: bool
    selectConnectedEdges: bool
    tooltipDelay: int
    zoomSpeed: int
    zoomView: bool
    
DefaultInteractionOptions: InteractionOptions = {
    'dragNodes': True,
    'dragView': True,
    'hideEdgesOnDrag': False,
    'hideEdgesOnZoom': False,
    'hideNodesOnDrag': False,
    'hover': False,
    'hoverConnectedEdges': True,
    'keyboard': DefaultKeyboardInteraction,
    'multiselect': False,
    'navigationButtons': False,
    'selectable': True,
    'selectConnectedEdges': True,
    'tooltipDelay': 300,
    'zoomSpeed': 1,
    'zoomView': True,
}
DefaultInteractionOptions = MappingProxyType(DefaultInteractionOptions) # type: ignore