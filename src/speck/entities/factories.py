"""Factories to easily create entities"""
from ..core import World
from ..components.dynamics import Position, Velocity, Acceleration, Mass, GravityConsumer, GravitySource
from ..components.rendering import RenderData, RenderType

def generate_moveable_agent(world: World,
                            x = 0, y = 0, z = 0,
                            vx =0, vy = 0, vz = 0,
                            ax =0, ay = 0, az = 0,
                            mass = 1):
    """Generate a point entity with position, velocity, acceleration, mass, and gravityconsumption"""
    new_eid = world.create_entity()
    world.add_component(new_eid, Position(x,y,z))
    world.add_component(new_eid, Velocity(vx,vy,vz))
    world.add_component(new_eid, Acceleration(ax,ay,az))
    world.add_component(new_eid, Mass(mass))
    world.add_component(new_eid, GravityConsumer())
    world.add_component(new_eid, RenderData())

def generate_body(world: World,
                    x = 0, y = 0, z = 0,
                    vx =0, vy = 0, vz = 0,
                    ax =0, ay = 0, az = 0,
                    mass = 1, radius = 1):
    """Generate an agent with position, velocity, acceleration, mass, and gravity consumption and gravity source"""
    new_eid = world.create_entity()
    world.add_component(new_eid, Position(x,y,z))
    world.add_component(new_eid, Velocity(vx,vy,vz))
    world.add_component(new_eid, Acceleration(ax,ay,az))
    world.add_component(new_eid, Mass(mass))
    world.add_component(new_eid, GravityConsumer())
    world.add_component(new_eid, GravitySource())
    world.add_component(new_eid, RenderData(render_type=RenderType.CIRCLE, radius=radius))