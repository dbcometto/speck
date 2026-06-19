"""Define the world engine"""
from __future__ import annotations
from typing import Self
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..components import Component
    from ..systems import System
    from ..sdk.agent import Agent

import time

from ..config import MAX_SUBSTEP_DELTA_T, MAX_SUBSTEPS
from .message_network import MessageNetwork

class World():
    """A world that holds data"""

    def __init__(self, timewarp = 1.0, debug_prints = False) -> None:
        """Initialize an empty world"""
        self._next_eid = 0
        self.components = {}  
        self.systems = []
        self.message_network = MessageNetwork()

        # World state
        self.time = 0
        self.timewarp = timewarp

        # Debugging state
        self.last_sim_dt = -1.0
        self.last_sub_steps = -1
        self.last_sub_dt = -1.0
        self.debug_prints = debug_prints


    # Entity Helpers

    def create_entity(self) -> int:
        """Establish a new eid and increment the counter"""
        eid = self._next_eid
        self._next_eid += 1
        return eid
    
    def remove_entity(self, eid: int) -> None:
        """Remove an entity from all component lists"""
        for store in self.components.values():
            store.pop(eid, None)
    
    def spawn(self, agent_class: type[Agent], **kwargs) -> int:
        """Update the ECS with an agent definition"""
        agent = agent_class(self, **kwargs)
        return agent._eid


    # Component Helpers

    def add_component(self, eid: int, component: Component) -> None:
        """Add a component to an entity"""
        t = type(component)
        if t not in self.components.keys():
            self.components[t] = {}
        self.components[t][eid] = component

    def get_component(self, component_type: type[Component]) -> dict:
        """Return the subdict for the specified component"""
        return self.components.get(component_type, {})


    # System Helpers

    def add_system(self, system: System):
        """Add a system to the world's list"""
        self.systems.append(system)

    def update(self, dt: float):
        sim_dt = dt*self.timewarp
        self.time += sim_dt

        steps = min(max(1, int(sim_dt / MAX_SUBSTEP_DELTA_T)), MAX_SUBSTEPS)
        sub_dt = sim_dt/steps
        for _ in range(steps):
            for system in self.systems:

                if self.debug_prints:
                     t = time.perf_counter()
                
                system.update(self,sub_dt)

                if self.debug_prints:
                    print(f"system {system}: {time.perf_counter()-t:.6f}s")

        # Debugging logging
        self.last_sim_dt = sim_dt
        self.last_sub_steps = steps
        self.last_sub_dt = sub_dt
    

    # TODO: save and load