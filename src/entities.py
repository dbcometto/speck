# Here we define all of the entities

from components import Position, Velocity, Acceleration, Forces
from components import Radius, Mass

# Next, create entities
class Entity:
    def __init__(self,entity_id):
        self.id = entity_id
        self.components = {}

    def add_component(self, component):
        self.components[type(component)] = component

    def get(self, component_type):
        return self.components.get(component_type)
    

# Now create specific objects
class Asteroid(Entity):
    def __init__(self,entity_id,position=(0,0),velocity=(0,0),component_forces={},radius=1,mass=1):
        super().__init__(entity_id)
        self.add_component(Position(*position))
        self.add_component(Velocity(*velocity))
        self.add_component(Acceleration())
        self.add_component(Forces(component_forces))
        self.add_component(Radius(radius))
        self.add_component(Mass(mass))