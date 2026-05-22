from types import MappingProxyType
from typing import Any, Literal, TypedDict


__all__ = 'PhysicsOptions', 'DefaultPhysicsOptions'


type JSFunc = Any


class BarnesHut(TypedDict, total=False):
    theta: float
    gravitationalConstant: int
    centralGravity: float
    springLength: int
    springConstant: float
    damping: float
    avoidOverlap: float

DefaultBarnesHut: BarnesHut = {
    'theta': 0.5,
    'gravitationalConstant': -2000,
    'centralGravity': 0.3,
    'springLength': 95,
    'springConstant': 0.04,
    'damping': 0.09,
    'avoidOverlap': 0.0,
}
DefaultBarnesHut = MappingProxyType(DefaultBarnesHut) # type: ignore

class ForceAtlas2Based(BarnesHut, total=False): ...

DefaultForceAtlas2Based: ForceAtlas2Based = {
    'theta': 0.5,
    'gravitationalConstant': -50,
    'centralGravity': 0.01,
    'springLength': 100,
    'springConstant': 0.08,
    'damping': 0.4,
    'avoidOverlap': 0.0,
}
DefaultForceAtlas2Based = MappingProxyType(DefaultForceAtlas2Based) # type: ignore


class Repulsion(TypedDict, total=False):
    nodeDistance: int
    centralGravity: float
    springLength: int
    springConstant: float
    damping: float

DefaultRepulsion: Repulsion = {
    'nodeDistance': 100,
    'centralGravity': 0.2,
    'springLength': 200,
    'springConstant': 0.05,
    'damping': 0.09,
}
DefaultRepulsion = MappingProxyType(DefaultRepulsion) # type: ignore


class HierarchicalRepulsion(Repulsion, total=False):
    avoidOverlap: float

DefaultHierarchicalRepulsion: HierarchicalRepulsion = {
    'nodeDistance': 120,
    'centralGravity': 0.01, #? docs say 0.0'
    'springLength': 100,
    'springConstant': 0.01,
    'damping': 0.09,
    'avoidOverlap': 0.0,
}
DefaultHierarchicalRepulsion = MappingProxyType(DefaultHierarchicalRepulsion) # type: ignore


class Stabilization(TypedDict, total=False):
    enabled: bool
    iterations: int
    updateInterval: int
    onlyDynamicEdges: bool
    fit: bool

DefaultStabilization: Stabilization = {
    'enabled': True,
    'iterations': 1000,
    'updateInterval': 50,
    'onlyDynamicEdges': False,
    'fit': True,
}
DefaultStabilization = MappingProxyType(DefaultStabilization) # type: ignore


class Wind(TypedDict, total=False):
    x: int
    y: int

DefaultWind: Wind = {
    'x': 0,
    'y': 0,
}
DefaultWind = MappingProxyType(DefaultWind) # type: ignore

class PhysicsOptions(TypedDict, total=False):
    enabled: bool
    barnesHut: BarnesHut
    forceAtlas2Based: ForceAtlas2Based
    repulsion: Repulsion
    hierarchicalRepulsion: HierarchicalRepulsion
    maxVelocity: float
    minVelocity: float
    solver: Literal['barnesHut', 'repulsion', 'hierarchicalRepulsion', 'forceAtlas2Based']
    stabilization: Stabilization | bool
    timestep: float
    adaptiveTimestep: bool
    wind: Wind | JSFunc
    
DefaultPhysicsOptions: PhysicsOptions = {
    'enabled': True,
    'barnesHut': DefaultBarnesHut,
    'forceAtlas2Based': DefaultForceAtlas2Based,
    'repulsion': DefaultRepulsion,
    'hierarchicalRepulsion': DefaultHierarchicalRepulsion,
    'maxVelocity': 50,
    'minVelocity': 0.1,
    'solver': 'barnesHut',
    'stabilization': DefaultStabilization,
    'timestep': 0.5,
    'adaptiveTimestep': True,
    'wind': DefaultWind,
}