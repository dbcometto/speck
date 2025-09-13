# Tests for factories

from speck.factories import create_rock, create_agent
from speck.components import Position, Velocity, Acceleration, Forces
from speck.components import Radius, Mass
from speck.components import Thruster
from speck.components import Behavior_Orbiter
from speck.components import RenderData


def test_create_rock():
    """Test rock factory function"""
    e = create_rock(0,position=(0,0),velocity=(0,0),component_forces=None,radius=1,mass=1)
    assert all([e.id                        == 0,
                e.get(Position).x           == 0,
                e.get(Position).y           == 0,
                e.get(Velocity).x           == 0,
                e.get(Velocity).y           == 0,
                e.get(Acceleration).x       == 0,
                e.get(Acceleration).y       == 0,
                e.get(Forces).components    == {},
                e.get(Forces).total_x       == 0,
                e.get(Forces).total_y       == 0,
                e.get(Radius).radius        == 1,
                e.get(Mass).mass            == 1,
                e.get(RenderData).shape,
                e.get(RenderData).color])
    
def test_create_agent():
    """Test agent factory function"""
    e = create_agent(0,position=(0,0),velocity=(0,0),component_forces=None,mass=1,radius=1,max_thrust=1)
    assert all([e.id                        == 0,
                e.get(Position).x           == 0,
                e.get(Position).y           == 0,
                e.get(Velocity).x           == 0,
                e.get(Velocity).y           == 0,
                e.get(Acceleration).x       == 0,
                e.get(Acceleration).y       == 0,
                e.get(Forces).components    == {},
                e.get(Forces).total_x       == 0,
                e.get(Forces).total_y       == 0,
                e.get(Radius).radius        == 1,
                e.get(Mass).mass            == 1,
                e.get(Thruster),
                e.get(RenderData).shape,
                e.get(RenderData).color])