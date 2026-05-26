from typing import (
    Any,
    TypedDict,
)

__all__ = 'Configuration', 'DefaultConfiguration'


class Configuration(TypedDict, total=False):
    enabled: bool
    filter: bool | str | list[str]
    container: Any
    showButton: bool


DefaultConfiguration: Configuration = {
    'enabled': True,
    'filter': True,
    'showButton': True,
}
