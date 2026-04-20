"""Define the world engine"""
from __future__ import annotations
from typing import Self
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..components import Component
    from ..systems import System

from ..config import MAX_SUBSTEP_DELTA_T, MAX_SUBSTEPS

class World():
    """A world that holds data"""

    def __init__(self, timewarp = 1.0) -> None:
        """Initialize an empty world"""
        self._next_eid = 0
        self.components = {}  
        self.systems = []

        # World state
        self.time = 0
        self.timewarp = timewarp

        # Debudding state
        self.last_sim_dt = -1.0
        self.last_sub_steps = -1
        self.last_sub_dt = -1.0


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
                system.update(self,sub_dt)

        # Debugging logging
        self.last_sim_dt = sim_dt
        self.last_sub_steps = steps
        self.last_sub_dt = sub_dt
    

    # TODO: save and load