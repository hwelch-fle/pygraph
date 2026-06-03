from importlib.util import find_spec, module_from_spec

from pygraph._adapters.protocols import DiGraphProto

if rustworkx := find_spec('rustworkx'):
    assert rustworkx.loader
    rustworkx = rustworkx.loader.exec_module(module_from_spec(rustworkx))
    if rustworkx is None:
        import rustworkx  # type: ignore
    DiGraph = rustworkx.PyDiGraph  # type: ignore
elif networkx := find_spec('networkx'):
    from .nx_adapters import *  # noqa: F403
else:
    from . import adapters as mod
    DiGraph = mod.DiGraph  # type: ignore

from typing import Any

DiGraph: type[DiGraphProto[Any, Any]]
