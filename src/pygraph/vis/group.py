from typing import TypedDict, TYPE_CHECKING
from types import MappingProxyType
from .node import NodeOptions


__all__ = 'GroupOptions', 'DefaultGroupOptions'


if TYPE_CHECKING:
    class GroupOptions(TypedDict, extra_items=NodeOptions):
        useDefaultGroups: bool
else:
    class GroupOptions(TypedDict):
        useDefaultGroups: bool

DefaultGroupOptions: GroupOptions = {
    'useDefaultGroups': True,
}
DefaultGroupOptions = MappingProxyType(DefaultGroupOptions) # type: ignore
