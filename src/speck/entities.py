# Here we define all of the entities

from .components import component_types
from .components import Position, Velocity, Acceleration, Forces
from .components import Radius, Mass
from .components import Thruster, Behavior_Orbiter
from .components import RenderData

# Next, create entities
class Entity:
    def __init__(self,entity_id):
        self.id = entity_id
        self.components = {}

    def add_component(self, component):
        self.components[type(component)] = component

    def remove_component(self,component_class):
        self.components.pop(component_class, None)

    def get(self, component_type):
        return self.components.get(component_type)
    
    def has(self, component_type):
        return True if self.get(component_type) else False
    
    def to_dict(self):
        """Convert entity to a JSON-serializable dictionary."""
        comp_dict = {}
        for comp_type, comp in self.components.items():
            # Store the component type as a string and use its own to_dict method
            comp_dict[comp_type.__name__] = comp.__dict__
        return {
                "id": self.id, 
                "components": comp_dict
                }
    
    @classmethod
    def from_dict(cls,data):
        """
        Reconstruct entity from dict.
        component_classes: dict mapping component type name (str) -> class
        """
        entity = cls(data["id"])
        for comp_name, comp_attrs in data["components"].items():
            # Use globals() to find the component class
            comp_cls = component_types[comp_name]  # assumes the class exists in the current module
            comp = comp_cls(**comp_attrs)    # generic constructor
            entity.add_component(comp)
        return entity
