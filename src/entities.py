# Here we define all of the entities

from components import Position, Velocity, Acceleration
from components import Radius

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
    def __init__(self,entity_id,position=(0,0),velocity=(0,0),acceleration=(0,0),radius=1):
        super().__init__(entity_id)
        self.add_component(Position(*position))
        self.add_component(Velocity(*velocity))
        self.add_component(Acceleration(*acceleration))
        self.add_component(Radius(radius))