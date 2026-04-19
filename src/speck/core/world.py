"""Define the world engine"""
from typing import Self

from ..components import Component

class World():
    """A world that holds data"""

    def __init__(self) -> Self:
        """Initialize an empty world"""
        self.components = {}
        self._next_eid = 0

    def create_entity(self) -> int:
        """Establish a new eid and increment the counter"""
        eid = self._next_eid
        self._next_eid += 1
        return eid
    
    def add_component(self, eid: int, component: Component) -> None:
        """Add a component to an entity"""
        t = type(component)
        if t not in self.components.keys():
            self.components[t] = {}
        self.components[t][eid] = component

    def get(self, component_type: type[Component]) -> dict:
        """Return the subdict for the specified component"""
        return self.components.get(component_type, {})

    def remove_entity(self, eid: int) -> None:
        """Remove an entity from all component lists"""
        for store in self.components.values():
            store.pop(eid, None)

    # TODO: save and load