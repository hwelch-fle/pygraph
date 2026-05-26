from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    TypedDict,
)

from .node import NodeOptions

__all__ = 'DefaultGroupOptions', 'GroupOptions'


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
