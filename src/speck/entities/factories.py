"""Factories to easily create entities"""
from ..core import World
from ..components.dynamics import Position, Velocity, Acceleration, Mass, GravityConsumer, GravitySource
from ..components.dynamics import Attitude, AngularVelocity, AngularAcceleration
from ..components.rendering import RenderData, RenderType
from ..components.functional import Identity
from ..components.assemblies import Assembly, PartIdentity, PORT_TYPE, PORT_DIRECTION
from ..components.assemblies import ThrusterBehavior, ScriptBehavior, AttitudeBehavior, ResourceBehavior
from ..scripts.default_scripts import RandomThrusterControl, RandomRCSControl







def generate_moveable_agent(world: World,
                            x = 0, y = 0, z = 0,
                            vx =0, vy = 0, vz = 0,
                            ax =0, ay = 0, az = 0,
                            qw=1, qx=0, qy=0, qz=0,
                            wx=0, wy=0, wz=0,
                            mass = 1, name = "Unnamed") -> int:
    """Generate an agent"""
    new_eid = world.create_entity()
    world.add_component(new_eid, Identity(name=name, classification="Agent"))
    world.add_component(new_eid, Position(x,y,z))
    world.add_component(new_eid, Velocity(vx,vy,vz))
    world.add_component(new_eid, Acceleration(ax,ay,az))
    world.add_component(new_eid, Attitude(qw, qx, qy, qz))
    world.add_component(new_eid, AngularVelocity(wx, wy, wz))
    world.add_component(new_eid, AngularAcceleration())
    world.add_component(new_eid, Mass(mass))
    world.add_component(new_eid, GravityConsumer())
    world.add_component(new_eid, RenderData())
    return new_eid



def generate_body(world: World,
                    x = 0, y = 0, z = 0,
                    vx =0, vy = 0, vz = 0,
                    ax =0, ay = 0, az = 0,
                    qw=1, qx=0, qy=0, qz=0,
                    wx=0, wy=0, wz=0,
                    mass = 1, radius = 1,
                    name = "Unnamed") -> int:
    """Generate a body"""
    new_eid = world.create_entity()
    world.add_component(new_eid, Identity(name=name, classification="Body"))
    world.add_component(new_eid, Position(x,y,z))
    world.add_component(new_eid, Velocity(vx,vy,vz))
    world.add_component(new_eid, Acceleration(ax,ay,az))
    world.add_component(new_eid, Attitude(qw, qx, qy, qz))
    world.add_component(new_eid, AngularVelocity(wx, wy, wz))
    world.add_component(new_eid, AngularAcceleration())
    world.add_component(new_eid, Mass(mass))
    world.add_component(new_eid, GravityConsumer())
    world.add_component(new_eid, GravitySource())
    world.add_component(new_eid, RenderData(render_type=RenderType.CIRCLE, radius=radius))
    return new_eid
