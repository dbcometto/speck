# This is used to easily create entities

from .entities import Entity

from .components import Position, Velocity, Acceleration, Forces
from .components import Radius, Mass
from .components import Thruster, Behavior_Orbiter
from .components import RenderData


def create_rock(entity_id,position=(0,0),velocity=(0,0),component_forces=None,radius=1,mass=1):
    """Spawns a rock"""
    e = Entity(entity_id=entity_id)
    e.add_component(Position(*position))
    e.add_component(Velocity(*velocity))
    e.add_component(Acceleration())
    e.add_component(Forces({} if component_forces is None else component_forces))
    e.add_component(Radius(radius))
    e.add_component(Mass(mass))
    e.add_component(RenderData(shape="circle",color='#666666'))
    return e

def create_agent(entity_id,position=(0,0),velocity=(0,0),component_forces=None,mass=1,radius=1,max_thrust=1):
    """Spawns an agent"""
    e = Entity(entity_id=entity_id)
    e.add_component(Position(*position))
    e.add_component(Velocity(*velocity))
    e.add_component(Acceleration())
    e.add_component(Forces({} if component_forces is None else component_forces))
    e.add_component(Radius(radius))
    e.add_component(Mass(mass))
    e.add_component(RenderData(shape="circle",color='#666666'))
    e.add_component(Thruster(max_thrust=max_thrust))
    e.add_component(RenderData(shape="rectangle",color="#4EDAC2"))
    return e