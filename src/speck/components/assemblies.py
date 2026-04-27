"""The assembly system"""
from abc import ABC
from enum import Enum

from .component import Component
from ..scripts import Script


# Assemblies

class Assembly(Component):
    """This entity contains parts and connections between them"""
    def __init__(self) -> None:
        self.parts: list[int] = []  # child eids
        self.edges: list[tuple[int, str, int, str]] = [] # (from_eid, from_port, to_eid, to_port) 

class FlowgraphLayout(Component):
    """Stores UI node positions for the flowgraph editor. Not simulation data."""
    def __init__(self):
        self.positions: dict[int, tuple[float, float]] = {}  # part_eid -> (wx, wy)
        self.flipped:   dict[int, bool] = {}                 # part_eid -> flipped

# Part Metadata

class PORT_TYPE(Enum):
    DATA = "data"
    POWER = "power"
    ITEM = "item"
    GRANULAR = "granular"
    FLUID = "fluid"

class PORT_DIRECTION(Enum):
    IN = "in"
    OUT = "out"

class PartIdentity(Component):
    """Metadata for a part in an assembly"""
    def __init__(self, assembly_eid: int | None = None, name: str = "", 
                 ports: list[tuple[str, PORT_TYPE, PORT_DIRECTION]] | None = None) -> None:
        self.assembly_eid = assembly_eid # of assembly
        self.name = name
        self.ports = ports if ports is not None else []
        self.port_values: dict[str, any] = {p[0]: None for p in self.ports}  # port_name -> current value


# Scripts

class ScriptBehavior(Component):
    """Assigns a behavior script to a part"""
    def __init__(self, script: Script, port_mapping: dict[str, str] | None = None) -> None:
        """Assigns a behavior script to a part"""
        self.script = script
        self.port_mapping = port_mapping if port_mapping is not None else {} # maps script port name -> real part port name


# Actuator Parts

class ThrusterBehavior(Component): # TODO: make able to choose axis
    """Assign a thruster that produces thrust to a part"""
    def __init__(self, control_port: str, fuel_storage_key: str, max_thrust: float = 1.0, axis = "+x"):
        """Assign a thruster that produces thrust to a part, axis is FLU"""
        self.control_port = control_port
        self.fuel_storage_key = fuel_storage_key
        self.max_thrust = max_thrust
        self.axis = axis

class AttitudeBehavior(Component):
    """Abstracted attitude control system - applies torque directly"""
    def __init__(self, control_port: str, max_torque: float = 1.0, axis = "+z") -> None:
        self.control_port = control_port
        self.max_torque = max_torque
        self.axis = axis



# Resource Parts

class ResourceBehavior(Component):
    def __init__(self, port_mapping: dict[str, str] | None = None, 
                 rates: dict[str, tuple[PORT_TYPE, float | None]] | None = None, 
                 capacities: dict[str, tuple[PORT_TYPE, float | None]] | None = None) -> None:
        """Give a part onboard storage connected to ports"""

        self.port_mapping = port_mapping if port_mapping is not None else {}    # storage_key: port_key
        self.rates = rates if rates is not None else {}                         # storage_key: type, rate
        self.capacities = capacities if capacities is not None else {}          # storage_key: type, max
        
        self.stored: dict[str, float] = {k: 0.0 if self.capacities[k][1] is not None else None for k in self.capacities} # current amount stored

