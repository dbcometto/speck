# Tests for components

from speck.components import Position, Velocity, Acceleration, Forces
from speck.components import Radius, Mass
from speck.components import Thruster
from speck.components import Behavior_Orbiter
from speck.components import RenderData

def test_position_init():
    """Tests init of Position"""
    pos = Position(0,0)
    assert pos.x == 0 and pos.y == 0

def test_velocity_init():
    """Tests init of Velocity"""
    vel = Velocity(0,0)
    assert vel.x == 0 and vel.y == 0

def test_acceleration_init():
    """Tests init of Acceleration"""
    acc = Acceleration(0,0)
    assert acc.x == 0 and acc.y == 0

def test_forces_empty_init():
    """Tests init of Forces when empty"""
    forces = Forces()
    assert all([forces.components == {}, forces.total_x == 0, forces.total_y == 0])

def test_forces_init():
    """Tests init of Forces with a force"""
    forces = Forces(components={"test_force":(1,1)})
    assert forces.components["test_force"]==(1,1)

def test_radius_init():
    """Tests init of Radius"""
    rad = Radius(1)
    assert rad.radius == 1

def test_mass_init():
    """Tests init of Mass"""
    mass = Mass(1)
    assert mass.mass == 1

def test_thruster_init():
    """Tests init of Thruster"""
    t = Thruster(1,1,1,1,1,1)
    assert all([t.max_thrust        == 1,
                t.thrust_x          == 1,
                t.thrust_y          == 1,
                t.desired_thrust_x  == 1,
                t.desired_thrust_y  == 1,
                t.throttle          == 1
                ])

def test_behavior_orbiter_init():
    """Tests init of Behavior_Orbiter"""
    b = Behavior_Orbiter(orbit_id = 0, orbit_distance= 1)
    assert all([b.orbit_id==0, b.orbit_distance==1])

def test_renderdata_init():
    """Tests init of RenderData"""
    r = RenderData(shape="rectangle",color="#DDBBCC")
    assert all([r.shape=="rectangle", r.color=="#DDBBCC"])