from typing import (
    Any,
    TypedDict,
)


class BaseTemplate(TypedDict):
    data: dict[str, Any]
    network: dict[str, Any]
    sankey: dict[str, Any]
