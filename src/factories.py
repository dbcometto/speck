# Here are the factory functions for entities

from entities import Entity

from components import Position, Velocity, Acceleration, Forces
from components import Radius, Mass, Width
from components import Thruster
from components import Behavior_Orbiter, Behavior_RandomThruster
from components import Render_Data

class Factory:
    def create_rock(entity_id,position=(0,0),velocity=(0,0),component_forces=None,radius=1,mass=1):
        e = Entity(entity_id=entity_id)

        e.add_component(Position(*position))
        e.add_component(Velocity(*velocity))
        e.add_component(Acceleration())
        e.add_component(Forces({} if component_forces is None else component_forces))
        e.add_component(Radius(radius))
        e.add_component(Mass(mass))
        e.add_component(Render_Data(shape="circle", color='#666666'))

        return e