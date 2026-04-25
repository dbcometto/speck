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






def generate_agent_with_thruster(world: World,
                            x=0, y=0, z=0,
                            vx=0, vy=0, vz=0,
                            ax=0, ay=0, az=0,
                            qw=1, qx=0, qy=0, qz=0,
                            wx=0, wy=0, wz=0,
                            mass=1, name="Unnamed Thruster Agent",
                            max_thrust=1.0) -> int:
    new_eid = generate_moveable_agent(world, x=x, y=y, z=z,
                                      vx=vx, vy=vy, vz=vz,
                                      ax=ax, ay=ay, az=az,
                                      qw=qw, qx=qx, qy=qy, qz=qz,
                                      wx=wx, wy=wy, wz=wz,
                                      mass=mass, name=name)
    world.add_component(new_eid, Assembly())
    assembly: Assembly = world.get_component(Assembly)[new_eid]

    # script part
    script_eid = world.create_entity()
    world.add_component(script_eid, PartIdentity(
        assembly_eid=new_eid, name="Script",
        ports=[("out", PORT_TYPE.DATA, PORT_DIRECTION.OUT)]
    ))
    world.add_component(script_eid, ScriptBehavior(
        script=RandomThrusterControl(), port_mapping={"out": "out"}
    ))
    assembly.parts.append(script_eid)

    # thruster part
    thruster_eid = world.create_entity()
    world.add_component(thruster_eid, PartIdentity(
        assembly_eid=new_eid, name="Thruster",
        ports=[
            ("control_in", PORT_TYPE.DATA,  PORT_DIRECTION.IN),
            ("fuel_in",    PORT_TYPE.FLUID, PORT_DIRECTION.IN),
        ]
    ))
    world.add_component(thruster_eid, ThrusterBehavior(
        control_port="control_in",
        fuel_storage_key="fuel",
        max_thrust=max_thrust
    ))
    world.add_component(thruster_eid, ResourceBehavior(
        port_mapping={"fuel": "fuel_in"},
        rates={"fuel": (PORT_TYPE.FLUID, None)},          # rate set by thruster at runtime
        capacities={"fuel": (PORT_TYPE.FLUID, 1000.0)}   # onboard tank
    ))
    world.get_component(ResourceBehavior).get(thruster_eid).stored["fuel"] = 1000.0
    assembly.parts.append(thruster_eid)

    assembly.edges.append((script_eid, "out", thruster_eid, "control_in"))

    return new_eid


def generate_agent_with_rcs_and_thruster(world: World,
                            x=0, y=0, z=0,
                            vx=0, vy=0, vz=0,
                            ax=0, ay=0, az=0,
                            qw=1, qx=0, qy=0, qz=0,
                            wx=0, wy=0, wz=0,
                            mass=1, name="Unnamed Thruster/RCS Agent",
                            max_thrust=1.0, max_torque=1.0) -> int:
    new_eid = generate_agent_with_thruster(world, x=x, y=y, z=z,
                                           vx=vx, vy=vy, vz=vz,
                                           ax=ax, ay=ay, az=az,
                                           qw=qw, qx=qx, qy=qy, qz=qz,
                                           wx=wx, wy=wy, wz=wz,
                                           mass=mass, name=name,
                                           max_thrust=max_thrust)
    assembly: Assembly = world.get_component(Assembly)[new_eid]

    # rcs script part
    script_eid = world.create_entity()
    world.add_component(script_eid, PartIdentity(
        assembly_eid=new_eid, name="RCS Script",
        ports=[("out", PORT_TYPE.DATA, PORT_DIRECTION.OUT)]
    ))
    world.add_component(script_eid, ScriptBehavior(
        script=RandomRCSControl(), port_mapping={"out": "out"}
    ))
    assembly.parts.append(script_eid)

    # attitude part
    rcs_eid = world.create_entity()
    world.add_component(rcs_eid, PartIdentity(
        assembly_eid=new_eid, name="RCS",
        ports=[("attitude_in", PORT_TYPE.DATA, PORT_DIRECTION.IN)]
    ))
    world.add_component(rcs_eid, AttitudeBehavior(
        control_port="attitude_in",
        max_torque=max_torque
    ))
    assembly.parts.append(rcs_eid)

    assembly.edges.append((script_eid, "out", rcs_eid, "attitude_in"))

    return new_eid