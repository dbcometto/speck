"""Part definitions for the Speck SDK"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import World
    from ..components.assemblies import Assembly

from ..components.assemblies import (
    PartIdentity, ThrusterBehavior, AttitudeBehavior,
    ResourceBehavior, ScriptBehavior, PORT_TYPE, PORT_DIRECTION
)


# Port and Part Handles

class PortHandle:
    """Reference to a named port on a part"""
    def __init__(self, part_eid: int, port_name: str):
        self.part_eid = part_eid
        self.port_name = port_name


class PartHandle:
    """Returned by Agent.add(), exposes ports as attributes"""
    def __init__(self, part_eid: int, ports: list[tuple]):
        self.part_eid = part_eid
        for name, _, _ in ports:
            setattr(self, name, PortHandle(part_eid, name))

class ComputerHandle(PartHandle):
    def __init__(self, part_eid, ports, script_behavior):
        super().__init__(part_eid, ports)
        self._sb = script_behavior
    
    def run(self, fn, period=1.0):
        self._sb.callables.append([fn, period, 0.0])
        return self


# Base Part

class Part:
    """Base class for all parts"""
    def _instantiate(self, world: World, assembly_eid: int, assembly: Assembly) -> PartHandle:
        """Enter the part into the ECS"""
        raise NotImplementedError


# Parts

class Thruster(Part):
    def __init__(self, max_thrust=1.0, axis="+x", fuel_buffer=100.0):
        self.max_thrust = max_thrust
        self.axis = axis
        self.fuel_buffer = fuel_buffer

    def _instantiate(self, world, assembly_eid, assembly) -> PartHandle:
        ports = [
            ("throttle_in", PORT_TYPE.DATA,  PORT_DIRECTION.IN),
            ("fuel_in",     PORT_TYPE.FLUID, PORT_DIRECTION.IN),
            ("power_in",    PORT_TYPE.POWER, PORT_DIRECTION.IN),
        ]

        eid = world.create_entity()

        world.add_component(eid, PartIdentity(assembly_eid=assembly_eid, name="Thruster", ports=ports))
        world.add_component(eid, ThrusterBehavior(
            control_port="throttle_in",
            fuel_storage_key="fuel",
            max_thrust=self.max_thrust,
            axis=self.axis
        ))
        world.add_component(eid, ResourceBehavior(
            port_mapping={"fuel": "fuel_in"},
            rates={"fuel": (PORT_TYPE.FLUID, None)},
            capacities={"fuel": (PORT_TYPE.FLUID, self.fuel_buffer)}
        ))

        assembly.parts.append(eid)

        return PartHandle(eid, ports)



class Tank(Part):
    def __init__(self, resource="fuel", capacity=500.0, port_type=PORT_TYPE.FLUID, fill=0.0, transfer_rate = 100000.0):
        self.resource = resource
        self.capacity = capacity
        self.port_type = port_type
        self.fill = fill
        self.transfer_rate = transfer_rate

    def _instantiate(self, world, assembly_eid, assembly) -> PartHandle:
        ports = [
            (f"{self.resource}_in",  self.port_type, PORT_DIRECTION.IN),
            (f"{self.resource}_out", self.port_type, PORT_DIRECTION.OUT),
        ]

        eid = world.create_entity()
        
        world.add_component(eid, PartIdentity(assembly_eid=assembly_eid, name=f"Tank({self.resource})", ports=ports))
        rb = ResourceBehavior(
            port_mapping={self.resource: f"{self.resource}_out"},
            rates={self.resource: (self.port_type, self.transfer_rate)},
            capacities={self.resource: (self.port_type, self.capacity)}
        )
        rb.stored[self.resource] = min(self.fill, self.capacity)
        world.add_component(eid, rb)

        assembly.parts.append(eid)

        return PartHandle(eid, ports)


class AttitudeController(Part):
    def __init__(self, max_torque=1.0, axis="+z"):
        self.max_torque = max_torque
        self.axis = axis

    def _instantiate(self, world, assembly_eid, assembly) -> PartHandle:
        ports = [
            ("control_in", PORT_TYPE.DATA, PORT_DIRECTION.IN),
        ]
        eid = world.create_entity()
        world.add_component(eid, PartIdentity(assembly_eid=assembly_eid, name="AttitudeController", ports=ports))
        world.add_component(eid, AttitudeBehavior(
            control_port="control_in",
            max_torque=self.max_torque,
            axis=self.axis
        ))
        assembly.parts.append(eid)
        return PartHandle(eid, ports)


class Computer(Part):
    def __init__(self, power=10.0, outputs=None, inputs=None):
        self.power = power
        self._outputs = outputs or []  # list of port name strings
        self._inputs  = inputs  or []
    
    def _instantiate(self, world, assembly_eid, assembly) -> PartHandle:
        ports = [("power_in", PORT_TYPE.POWER, PORT_DIRECTION.IN)]
        ports += [(name, PORT_TYPE.DATA, PORT_DIRECTION.OUT) for name in self._outputs]
        ports += [(name, PORT_TYPE.DATA, PORT_DIRECTION.IN)  for name in self._inputs]
        
        eid = world.create_entity()
        world.add_component(eid, PartIdentity(assembly_eid=assembly_eid, name="Computer", ports=ports))
        sb = ScriptBehavior()
        world.add_component(eid, sb)

        assembly.parts.append(eid)

        return ComputerHandle(eid, ports, sb)