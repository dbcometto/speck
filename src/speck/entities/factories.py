"""Factories to easily create entities"""
from ..core import World
from ..components.dynamics import Position, Velocity, Acceleration, Mass, GravityConsumer, GravitySource
from ..components.dynamics import Attitude, AngularVelocity, AngularAcceleration
from ..components.rendering import RenderData, RenderType
from ..components.functional import Identity
from ..components.assemblies import Assembly, PartIdentity, PORT_TYPE
from ..components.assemblies import ThrusterBehavior, ScriptBehavior, RCSBehavior
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






def generate_agent_with_thruster(world: World,
                            x = 0, y = 0, z = 0,
                            vx =0, vy = 0, vz = 0,
                            ax =0, ay = 0, az = 0,
                            qw=1, qx=0, qy=0, qz=0,
                            wx=0, wy=0, wz=0,
                            mass = 1, name = "Unnamed Thruster Agent",
                            max_thrust=1.0) -> int:
    """Generate an agent with a thruster"""
    new_eid = generate_moveable_agent(world, x=x, y=y, z=z,
                                   vx=vx, vy=vy, vz=vz,
                                   ax=ax, ay=ay, az=az,
                                   qw=qw, qx=qx, qy=qy, qz=qz,
                                   wx=wx, wy=wy, wz=wz,
                                   mass=mass, name=name)
    world.add_component(new_eid, Assembly())

    assembly: Assembly = world.get_component(Assembly)[new_eid]

    # create script part
    script_part_eid = world.create_entity()
    world.add_component(script_part_eid, PartIdentity(
        assembly_eid=new_eid,
        name="Script",
        ports=[("out", PORT_TYPE.DATA)]
    ))
    world.add_component(script_part_eid, ScriptBehavior(script=RandomThrusterControl(), port_mapping={"out":"out"}))
    assembly.parts.append(script_part_eid)

    # create thruster part
    thruster_eid = world.create_entity()
    world.add_component(thruster_eid, PartIdentity(
        assembly_eid=new_eid,
        name="Thruster",
        ports=[("control_in", PORT_TYPE.DATA), ("fuel_in", PORT_TYPE.FLUID)]
    ))
    world.add_component(thruster_eid, ThrusterBehavior(
        control_port="control_in",
        fuel_port="fuel_in",
        max_thrust=max_thrust
    ))
    assembly.parts.append(thruster_eid)

    # connect script to thruster
    assembly.edges.append((script_part_eid, "out", thruster_eid, "control_in"))

    return new_eid












def generate_agent_with_rcs_and_thruster(world: World,
                            x = 0, y = 0, z = 0,
                            vx =0, vy = 0, vz = 0,
                            ax =0, ay = 0, az = 0,
                            qw=1, qx=0, qy=0, qz=0,
                            wx=0, wy=0, wz=0,
                            mass = 1, name = "Unnamed Thruster/RCS Agent",
                            max_thrust=1.0, max_torque=1.0) -> int:
    """Generate an agent with a thruster"""
    new_eid = generate_agent_with_thruster(world, x=x, y=y, z=z,
                                   vx=vx, vy=vy, vz=vz,
                                   ax=ax, ay=ay, az=az,
                                   qw=qw, qx=qx, qy=qy, qz=qz,
                                   wx=wx, wy=wy, wz=wz,
                                   mass=mass, name=name,
                                   max_thrust=max_thrust)
    assembly: Assembly = world.get_component(Assembly)[new_eid]

    # create script part
    script_part_eid = world.create_entity()
    world.add_component(script_part_eid, PartIdentity(
        assembly_eid=new_eid,
        name="Script",
        ports=[("out", PORT_TYPE.DATA)]
    ))
    world.add_component(script_part_eid, ScriptBehavior(script=RandomRCSControl(), port_mapping={"out":"out"}))
    assembly.parts.append(script_part_eid)

    # create thruster part
    rcs_eid = world.create_entity()
    world.add_component(rcs_eid, PartIdentity(
        assembly_eid=new_eid,
        name="RCS",
        ports=[("attitude_in", PORT_TYPE.DATA)]
    ))
    world.add_component(rcs_eid, RCSBehavior(
        attitude_port="attitude_in",
        max_torque=max_torque
    ))
    assembly.parts.append(rcs_eid)

    # connect script to thruster
    assembly.edges.append((script_part_eid, "out", rcs_eid, "attitude_in"))