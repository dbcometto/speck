"""Agent base class for the Speck SDK"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import World

from abc import ABC, abstractmethod

from ..components.dynamics import Position, Velocity, Acceleration, Mass, GravityConsumer
from ..components.dynamics import Attitude, AngularVelocity, AngularAcceleration
from ..components.rendering import RenderData
from ..components.functional import Identity
from ..components.assemblies import Assembly


class Agent(ABC):
    """Base class for all agent definitions. Subclass and implement define()."""

    def __init__(self, world: World,
                 x=0.0, y=0.0, z=0.0,
                 vx=0.0, vy=0.0, vz=0.0,
                 qw=1.0, qx=0.0, qy=0.0, qz=0.0,
                 mass=1.0, name="Unnamed", classification="Agent") -> None:

        self._world = world

        # Create base entity
        self._eid = world.create_entity()

        # Base components
        world.add_component(self._eid, Identity(name=name, classification=classification))
        world.add_component(self._eid, Position(x, y, z))
        world.add_component(self._eid, Velocity(vx, vy, vz))
        world.add_component(self._eid, Acceleration())
        world.add_component(self._eid, Attitude(qw, qx, qy, qz))
        world.add_component(self._eid, AngularVelocity())
        world.add_component(self._eid, AngularAcceleration())
        world.add_component(self._eid, Mass(mass))
        world.add_component(self._eid, GravityConsumer())
        world.add_component(self._eid, RenderData())

        # Assembly
        self._assembly = Assembly()
        world.add_component(self._eid, self._assembly)

        # Call player definition
        self.define()




    # Define - User Function

    @abstractmethod
    def define(self) -> None:
        """Override to define hardware and software. Called once at construction."""
        pass



    # Helpers

    def add(self, part) -> object:
        """Add a part to this agent, returns a PartHandle"""
        return part._instantiate(self._world, self._eid, self._assembly)

    def connect(self, out_port, in_port) -> None:
        """Connect two ports"""
        self._assembly.edges.append(
            (out_port.part_eid, out_port.port_name,
             in_port.part_eid,  in_port.port_name)
        )