from typing import TypedDict

from pygraph import EdgeRecord, NetworkOptions, NodeRecord

type CSSVal = int | str
type CSSColor = str


class NetworkStyle(TypedDict, total=False):
    width: CSSVal
    """Network container width"""
    height: CSSVal
    """Network container height"""
    background: CSSColor
    """Network container background color"""


class NetworkSchema(TypedDict, total=False):
    nodes: list[NodeRecord]
    """list of Nodes to include in the network"""
    edges: list[EdgeRecord]
    """list of Edges to include in the network"""
    options: NetworkOptions
    """Base Network options"""
    title: str
    """Page title"""
    google_fonts: list[str]
    """Google fonts to include from CDN"""
    font_awesome: bool
    """Set to True to include Font Awesome CDN resources (for icon shape)"""
    hover_edge_labels: bool
    """Only show edge labels when hovering over a Node or Edge"""
    style: NetworkStyle
    """Base style of the Network container"""


class ProgressorStyle(TypedDict, total=False):
    width: CSSVal
    """Progress Bar width"""
    right: CSSVal
    """Progress Bar offset from right of window"""
    bottom: CSSVal
    """Progress Bar offset from bottom of window"""
    background: CSSColor
    """Background color for Progress Bar"""
    color: CSSColor
    """Fill color for Progress Bar"""
    radius: CSSVal
    """Corner radius of progress bar"""
    blur: CSSVal
    """Optional blur to apply to Progress Bar background"""


# May be expanded later
class ProgressorSchema(TypedDict, total=False):
    enabled: bool
    """Pass anything to this to enable the Progress Bar with defaults"""
    style: ProgressorStyle
    """Progress Bar styling"""


class NodeSelectorSchema(TypedDict, total=False):
    """See: https://tom-select.js.org/docs/api/"""
    enabled: bool
    """Set to False to disable the selector"""
    placeholder_text: str
    """Placeholder text for the search box"""
    max_items: int
    """Max items to show in dropdown"""
    max_options: int
    """Maximum selection options"""
    value_field: str
    """Field to use as option value"""
    label_field: str
    """Field to use as label value"""
    search_field: str
    """Field to use as search value"""
    sort_field: str
    """Field to sort by"""
    unique: bool
    """Force the options to be unique (will select all matching network objects)"""
    reset_on_clear: bool
    """Reset the network when the selection is cleared"""


# Currently Identical to NodeSelectorSchema
class EdgeSelectorSchema(NodeSelectorSchema):
    """See: https://tom-select.js.org/docs/api/"""


class SelectorSchema(TypedDict, total=False):
    enabled: bool
    """Pass anything to this to enable the Selectors with defaults"""
    node: NodeSelectorSchema
    """Node selector options"""
    edge: EdgeSelectorSchema
    """Edge selector options"""


class BaseTemplateOptions(TypedDict, total=False):
    network: NetworkSchema
    """Network options"""
    progressor: ProgressorSchema
    """Progress Bar options"""
    selectors: SelectorSchema
    """Search/Selector options"""
