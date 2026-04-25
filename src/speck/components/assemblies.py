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

class PartIdentity(Component):
    """Metadata for a part in an assembly"""
    def __init__(self, assembly_eid: int | None = None, name: str = "", 
                 ports: list[tuple[str, PORT_TYPE]] | None = None) -> None:
        self.assembly_eid = assembly_eid # of assembly
        self.name = name
        self.ports = ports if ports is not None else []
        self.port_values: dict[str, any] = {p[0]: None for p in self.ports}  # port_name -> current value


# Scripts

class ScriptBehavior(Component):
    """Assigns a behavior scriptto a part"""
    def __init__(self, script: Script, port_mapping: dict[str, str] | None = None) -> None:
        """Assigns a behavior script to a part"""
        self.script = script
        self.port_mapping = port_mapping if port_mapping is not None else {} # maps script port name -> real part port name




# Actuator Parts

class ThrusterBehavior(Component): # TODO: make able to choose axis
    """Assign a thruster that produces thrust to a part"""
    def __init__(self, control_port: str, fuel_port: str, max_thrust: float = 1.0):
        self.control_port = control_port
        self.fuel_port = fuel_port
        self.max_thrust = max_thrust
        # self.throttle = 0.0

class RCSBehavior(Component): # TODO: translation # TODO: documentation for user on ports
    """Abstracted attitude control system - applies torque and translation directly"""
    def __init__(self, attitude_port: str, max_torque: float = 1.0) -> None:
        self.attitude_port = attitude_port
        self.max_torque = max_torque
        # self.torque_z = 0.0
        # TODO: 3D



# Resource Parts

