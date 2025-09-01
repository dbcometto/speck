# Here we define all of the entities

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
        self.add_component(Radius(radius=width))
        self.add_component(Thruster(max_thrust=max_thrust))

class Orbiter(Agent):
    def __init__(self,entity_id,orbit_id,position=(0,0),velocity=(0,0),component_forces=None,mass=1,width=1,max_thrust=1):
        super().__init__(entity_id,position,velocity,component_forces,mass,width,max_thrust)
        self.add_component(Behavior_Orbiter(orbit_id))