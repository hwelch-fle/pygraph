from typing import Literal, TypedDict, Any
from types import MappingProxyType

# Same options as Edge
from .edge import (
    Font,
    Scaling, DefaultScaling,
    Shadow, DefaultShadow,
    WidthConstraint,
)


__all__ = 'NodeOptions', 'NodeRecord', 'DefaultNodeOptions'


type JSFunc = Any
type HexColor = str
type RGBColor = str
type RGBAColor = str
type HTMLColor = str


class Chosen(TypedDict, total=False):
    node: bool | JSFunc
    label: bool | JSFunc

DefaultChosen: Chosen = {}
DefaultChosen = MappingProxyType(DefaultChosen) # type: ignore


class Highlight(TypedDict, total=False):
    border: HexColor
    background: HexColor

DefaultHighlight: Highlight = {
    'border': '#2B7CE9',
    'background': '#D2E5FF',
}
DefaultHighlight = MappingProxyType(DefaultHighlight) # type: ignore


class Hover(Highlight): ...

DefaultHover: Hover = {
    'border': '#2B7CE9',
    'background': '#D2E5FF',
}
DefaultHover = MappingProxyType(DefaultHover) # type: ignore


class Color(TypedDict, total=False):
    border: HexColor
    background: HexColor
    highlight: Highlight
    hover: Hover
    
DefaultColor: Color = {
    'border': '#2B7CE9',
    'background': '#D2E5FF',
    'highlight': DefaultHighlight,
    'hover': DefaultHover,
}
DefaultColor = MappingProxyType(DefaultColor) # type: ignore


class Fixed(TypedDict, total=False):
    x: bool
    y: bool
    
DefaultFixed: Fixed = {
    'x': False,
    'y': False,
}
DefaultFixed = MappingProxyType(DefaultFixed) # type: ignore


class HeightConstraint(TypedDict, total=False):
    minimum: int
    valign: Literal['top', 'middle', 'bottom']

DefaultHeightConstraint: HeightConstraint = {
    'valign': 'middle',
}
DefaultHeightConstraint = MappingProxyType(DefaultHeightConstraint) # type: ignore


class Icon(TypedDict, total=False):
    face: str
    code: str
    size: int
    color: HexColor
    weight: str | int

DefaultIcon: Icon = {
    'face': 'FontAwesome',
    'size': 50,
    'color': '#2B7CE9',
}
DefaultIcon = MappingProxyType(DefaultIcon) # type: ignore


class Image(TypedDict, total=False):
    unselected: str
    selected: str
    
DefaultImage: Image = {}
DefaultImage = MappingProxyType(DefaultImage) # type: ignore


class Margin(TypedDict, total=False):
    top: int
    bottom: int
    left: int
    right: int
    
DefaultMargin: Margin = {
    'top': 5,
    'bottom': 5,
    'left': 5,
    'right': 5,
}
DefaultMargin = MappingProxyType(DefaultMargin) # type: ignore


class ImagePadding(Margin, total=False): ...
    
DefaultImagePadding: ImagePadding = {
    'top': 0,
    'bottom': 0,
    'left': 0,
    'right': 0,
}
DefaultImagePadding = MappingProxyType(DefaultImagePadding) # type: ignore


class ShapeProperties(TypedDict, total=False):
    borderDashes: bool | list[int]
    borderRadius: int
    interpolation: bool
    useImageSize: bool
    useBorderWithImage: bool
    coordinateOrigin: Literal['center', 'top-left']
    
DefaultShapeProperties: ShapeProperties = {
    'borderDashes': False,
    'borderRadius': 6,
    'interpolation': True,
    'useImageSize': False,
    'useBorderWithImage': False,
    'coordinateOrigin': 'center',
}
DefaultShapeProperties = MappingProxyType(DefaultShapeProperties) # type: ignore


class NodeOptions(TypedDict, total=False):
    borderWidth: int
    borderWidthSelected: int
    brokenImage: str
    chosen: Chosen | bool
    color: Color | str
    ctxRenderer: JSFunc
    opacity: float
    fixed: Fixed | bool
    font: Font | str | bool # ?
    group: str
    heightConstraint: HeightConstraint | int | bool
    hidden: bool
    icon: Icon
    image: Image | str
    imagePadding: ImagePadding | int
    labelHighlightBold: bool
    margin: Margin | int
    mass: int
    physics: bool
    scaling: Scaling
    shadow: Shadow | bool
    shape: Literal[
        # Label inside
        'ellipse', 'circle', 'database', 'box', 'text', 
        # Label Outside
        'image', 'circularImage', 'diamond', 'dot', 'star', 'triangle', 'triangleDown', 'hexagon', 'square', 'icon'
    ]
    shapeProperties: ShapeProperties
    size: int
    widthConstraint: WidthConstraint | int | bool
    x: int
    y: int
    title: str
    value: int
    level: int
    label: str

    
DefaultNodeOptions: NodeOptions = {
    'borderWidth': 1,
    'borderWidthSelected': 2,
    'chosen': DefaultChosen,
    'color': DefaultColor,
    'font': False,
    'heightConstraint': False,
    'hidden': False,
    'icon': DefaultIcon,
    'imagePadding': 0,
    'labelHighlightBold': True,
    'margin': 5,
    'mass': 1,
    'physics': True,
    'scaling': DefaultScaling,
    'shadow': DefaultShadow,
    'shape': 'ellipse',
    'shapeProperties': DefaultShapeProperties,
    'size': 50,
    'widthConstraint': False,
}
DefaultNodeOptions = MappingProxyType(DefaultNodeOptions) # type: ignore


class NodeRecord(NodeOptions):
    id: int | str
