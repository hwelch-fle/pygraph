from __future__ import annotations

from types import MappingProxyType
from typing import (
    Any,
    Literal,
    NotRequired,
    TypedDict,
)

__all__ = 'DefaultEdgeOptions', 'EdgeOptions', 'EdgeRecord'


# Color types for disambiguation of which colorstrings are allowed
type JSFunc = Any
type HexColor = str
type RGBColor = str
type RGBAColor = str


# Type Definitions
#
# NOTE: Currently all defaults are created as MappingProxyTypes, but
#       they should be migrated to frozendict once that is available
#       and common

class Arrow(TypedDict, total=False):
    enabled: bool
    imageHeight: int
    imageWidth: int
    scaleFactor: float
    src: str
    type: Literal['arrow', 'bar', 'circle', 'image']

DefaultArrow: Arrow = {
    'enabled': False,
    'scaleFactor': 1.0,
    'type': 'arrow',
}
DefaultArrow = MappingProxyType(DefaultArrow) # type: ignore


Arrows = TypedDict(
    'Arrows',
    {
        'to': Arrow | bool,
        'middle': Arrow | bool,
        'from': Arrow | bool,
    },
    total=False
)

DefaultArrows: Arrows = {
    'to': DefaultArrow,
    'middle': DefaultArrow,
    'from': DefaultArrow,
}
DefaultArrows = MappingProxyType(DefaultArrows) # type: ignore


ArrowOffset = TypedDict(
    'ArrowOffset',
    {
        'to': float,
        'from': float,
        'arrowStrikethrough': bool,
    },
    total=False
)

DefaultArrowOffset: ArrowOffset = {
    'to': 0.0,
    'from': 0.0,
    'arrowStrikethrough': True,
}
DefaultArrow = MappingProxyType(DefaultArrow) # type: ignore


class Chosen(TypedDict, total=False):
    edge: bool | Any
    label: bool | Any

DefaultChosen: Chosen = {}
DefaultChosen = MappingProxyType(DefaultChosen) # type: ignore


class Color(TypedDict, total=False):
    color: HexColor
    highlight: HexColor
    hover: HexColor
    inherit: bool | Literal['from', 'to', 'both']
    opacity: float

DefaultColor: Color = {
    'color': '#848484',
    'highlight': '#848484',
    'hover': '#848484',
    'inherit': 'from',
    'opacity': 1.0,
}
DefaultColor = MappingProxyType(DefaultColor) # type: ignore


class FontClass(TypedDict, total=False):
    color: HexColor
    size: int
    face: str
    mod: str
    vadjust: int

DefaultBoldFont: FontClass = {
    'color': '#343434',
    'size': 14,
    'face': 'arial',
    'mod': 'bold',
    'vadjust': 0,
}
DefaultBoldFont = MappingProxyType(DefaultBoldFont) # type: ignore

DefaultItalFont: FontClass = {
    'color': '#343434',
    'size': 14,
    'face': 'arial',
    'mod': 'ital',
    'vadjust': 0,
}
DefaultItalFont = MappingProxyType(DefaultItalFont) # type: ignore

DefaultBoldItalFont: FontClass = {
    'color': '#343434',
    'size': 14,
    'face': 'arial',
    'mod': 'bold',
    'vadjust': 0,
}
DefaultBoldItalFont = MappingProxyType(DefaultBoldItalFont) # type: ignore

DefaultMonoFont: FontClass = {
    'color': '#343434',
    'size': 15,
    'face': 'courier new',
    'mod': '',
    'vadjust': 2,
}
DefaultMonoFont = MappingProxyType(DefaultMonoFont) # type: ignore


class Font(TypedDict, total=False):
    color: HexColor
    size: int
    face: str
    background: str | None
    strokeWidth: int
    strokeColor: HexColor
    align: Literal['horizontal', 'top', 'middle', 'bottom']
    vadjust: int
    multi: bool | Literal['html', 'markdown', 'md']
    bold: FontClass | bool | str
    ital: FontClass | bool | str
    boldital: FontClass | bool | str
    mono: FontClass | bool | str

DefaultFont: Font = {
    'color': '#343434',
    'size': 14,
    'face': 'arial',
    'strokeWidth': 2,
    'strokeColor': '#ffffff',
    'align': 'horizontal',
    'vadjust': 0,
    'multi': False,
    'bold': False,
    'ital': False,
    'boldital': False,
    'mono': False,
}
DefaultFont = MappingProxyType(DefaultFont) # type: ignore


class Label(TypedDict, total=False):
    enabled: bool
    min: int
    max: int
    maxVisible: int
    drawThreshold: int

DefaultLabel: Label = {
    'enabled': False,
    'min': 14,
    'max': 30,
    'maxVisible': 30,
    'drawThreshold': 5,
}
DefaultLabel = MappingProxyType(DefaultLabel) # type: ignore


class Scaling(TypedDict, total=False):
    min: int
    max: int
    label: Label
    customScalingFunction: Any
    selectionWidth: int | Any

# Default scaling function as a string (probably best to not set this?)
_sfunc = """function (min,max,total,value) {
  if (max === min) {
    return 0.5;
  }
  else {
    var scale = 1 / (max - min);
    return Math.max(0,(value - min)*scale);
  }
}"""

DefaultScaling: Scaling = {
    'min': 1,
    'max': 15,
    'label': DefaultLabel,
    #'customScalingFunction': _sfunc,
    'selectionWidth': 1,
}
DefaultScaling = MappingProxyType(DefaultScaling) # type: ignore


class SelfReference(TypedDict, total=False):
    size: int
    angle: float
    renderBehindTheNode: bool

DefaultSelfReference: SelfReference = {
    'size': 20,
    'angle': 0.7853981633974483, # pi/4 rad
    'renderBehindTheNode': True,
}
DefaultSelfReference = MappingProxyType(DefaultSelfReference) # type: ignore


class Shadow(TypedDict, total=False):
    enabled: bool
    color: HexColor | RGBColor | RGBAColor
    size: int
    x: int
    y: int

DefaultShadow: Shadow = {
    'enabled': False,
    'color': 'rgba(0,0,0,0.5)',
    'size': 10,
    'x': 5,
    'y': 5,
}
DefaultShadow = MappingProxyType(DefaultShadow) # type: ignore


class Smoothing(TypedDict, total=False):
    enabled: bool
    type: Literal['dynamic', 'continuous', 'discrete', 'diagonalCross', 'straightCross',
                  'horizontal', 'vertical', 'curvedCW', 'curvedCCW', 'cubicBezier']
    forceDirection: bool | Literal['horizontal', 'vertical', 'none']
    roundness: float

DefaultSmoothing: Smoothing = {
    'enabled': True,
    'type': 'dynamic',
    'forceDirection': False,
    'roundness': 0.5,
}
DefaultSmoothing = MappingProxyType(DefaultSmoothing) # type: ignore

class WidthConstraint(TypedDict, total=False):
    maximum: int

DefaultWidthConstraint: WidthConstraint = {}
DefaultWidthConstraint = MappingProxyType(DefaultWidthConstraint) # type: ignore

class EdgeOptions(TypedDict, total=False):
    arrows: Arrows | str
    endPointOffset: ArrowOffset
    arrowStrikethrough: bool
    chosen: Chosen | bool
    color: Color | str
    dashes: bool | list[int]
    font: Font | str
    hidden: bool
    hoverWidth: float | JSFunc
    label: str
    labelHighlightBold: bool
    length: float
    physics: bool
    scaling: Scaling
    selectionWidth: int | JSFunc
    #selfReferenceSize: None #deprecated
    selfReference: SelfReference
    shadow: Shadow | bool
    smooth: Smoothing | bool
    title: str
    value: float
    width: int
    widthConstraint: WidthConstraint | int | bool

DefaultEdgeOptions: EdgeOptions = {
    'arrows': DefaultArrows,
    'endPointOffset': DefaultArrowOffset,
    'arrowStrikethrough': True,
    'chosen': DefaultChosen,
    'color': DefaultColor,
    'dashes': False,
    'font': DefaultFont,
    'hidden': False,
    'hoverWidth': 0.5,
    'labelHighlightBold': True,
    'physics': True,
    'scaling': DefaultScaling,
    'selectionWidth': 1,
    'selfReference': DefaultSelfReference,
    'shadow': DefaultShadow,
    'smooth': DefaultSmoothing,
    'width': 1,
    'widthConstraint': False,
}
DefaultEdgeOptions = MappingProxyType(DefaultEdgeOptions) # type: ignore

_Edge = TypedDict(
    '_Edge',
    {
        'from': int | str,
        'to': int | str,
    },
)

# Final edge definition
class EdgeRecord(_Edge, EdgeOptions):
    id: NotRequired[str]
