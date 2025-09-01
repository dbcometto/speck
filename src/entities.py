# Here we define all of the entities

from components import component_types
from components import Position, Velocity, Acceleration, Forces
from components import Radius, Mass, Width
from components import Thruster, Behavior_Orbiter

# Next, create entities
class Entity:
    def __init__(self,entity_id):
        self.id = entity_id
        self.components = {}

    def add_component(self, component):
        self.components[type(component)] = component

    def remove_component(self,component):
        self.components.pop(type(component), None)

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
                "class": type(self).__name__,
                "id": self.id, 
                "components": comp_dict
                }
    
    @classmethod
    def from_dict(cls,data):
        """
        Reconstruct entity from dict.
        component_classes: dict mapping component type name (str) -> class
        """
        entity_cls = entity_types[data["class"]]
        entity = entity_cls(data["id"])
        for comp_name, comp_attrs in data["components"].items():
            # Use globals() to find the component class
            comp_cls = component_types[comp_name]  # assumes the class exists in the current module
            comp = comp_cls(**comp_attrs)    # generic constructor
            entity.add_component(comp)
        return entity


    

    
    
    

# Now create specific objects
class Rock(Entity):
    def __init__(self,entity_id,position=(0,0),velocity=(0,0),component_forces=None,radius=1,mass=1):
        super().__init__(entity_id)
        self.add_component(Position(*position))
        self.add_component(Velocity(*velocity))
        self.add_component(Acceleration())
        self.add_component(Forces({} if component_forces is None else component_forces))
        self.add_component(Radius(radius))
        self.add_component(Mass(mass))


class Agent(Rock):
    def __init__(self,entity_id,position=(0,0),velocity=(0,0),component_forces=None,mass=1,width=1,max_thrust=1):
        super().__init__(entity_id,position,velocity,component_forces,mass)
        self.add_component(Width(width=width))
        self.add_component(Radius(radius=width*1.4/2))
        self.add_component(Thruster(max_thrust=max_thrust))

class Orbiter(Agent):
    def __init__(self,entity_id,orbit_id,position=(0,0),velocity=(0,0),component_forces=None,mass=1,width=1,max_thrust=1):
        super().__init__(entity_id,position,velocity,component_forces,mass,width,max_thrust)
        self.add_component(Behavior_Orbiter(orbit_id))



entity_types = {
    "Rock"      : Rock,
    "Agent"     : Agent,
    "Orbiter"   : Orbiter,
}