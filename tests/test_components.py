# Tests for components

from speck.components import Position, Velocity, Acceleration, Forces
from speck.components import Radius, Mass, Width
from speck.components import Thruster
from speck.components import Behavior_Orbiter, Behavior_RandomThruster
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
    """Tests init of Acceleration"""
    forces = Forces()
    assert all(forces.components == {}, forces.total_x == 0, forces.total_y == 0)