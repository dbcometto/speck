# Tests for systems

from speck.entities import Entity
from speck.components import Position, Velocity, Acceleration, Forces
from speck.components import Mass
from speck.factories import create_rock

from speck.systems import MovementSystem, ForceSystem, GravitySystem

def test_movementSystem_init():
    """Test init of MovementSystem"""
    sys = MovementSystem(dt=1)
    assert sys.dt == 1

def test_movementSystem_1():
    """Test movement system with static entity"""
    e = Entity(0)
    e.add_component(Position(0,0))
    e.add_component(Velocity(0,0))
    e.add_component(Acceleration(0,0))

    elist = [e]
    edict = {0:e}

    sys = MovementSystem()
    sys.update(elist,edict)

    assert e.get(Position).x==0 and e.get(Position).y==0

def test_movementSystem_2():
    """Test movement system with static velocity"""
    e = Entity(0)
    e.add_component(Position(0,0))
    e.add_component(Velocity(1,0))
    e.add_component(Acceleration(0,0))

    elist = [e]
    edict = {0:e}

    sys = MovementSystem()
    sys.update(elist,edict)

    assert e.get(Position).x==1 and e.get(Position).y==0

def test_movementSystem_3():
    """Test movement system with static acceleration"""
    e = Entity(0)
    e.add_component(Position(0,0))
    e.add_component(Velocity(0,0))
    e.add_component(Acceleration(1,0))

    elist = [e]
    edict = {0:e}

    sys = MovementSystem()
    sys.update(elist,edict)

    assert e.get(Velocity).x==1 and e.get(Velocity).y==0


def test_forceSystem():
    """Test force system"""
    e = Entity(0)
    e.add_component(Forces(components={"test_force":(1,1)}))

    elist = [e]
    edict = {0:e}

    sys = ForceSystem()
    sys.update(elist,edict)

    assert e.get(Forces).total_x==1 and e.get(Forces).total_y==1


# def test_gravitySystem():
#     """Test gravity system simply... not working right now"""
#     # e0 = Entity(0)
#     # e0.add_component(Position(0,0))
#     # e0.add_component(Mass(1e6))
#     # e0.add_component(Forces())
    
#     # e1 = Entity(1)
#     # e1.add_component(Position(1e3,0))
#     # e1.add_component(Mass(1e6))
#     # e1.add_component(Forces())

#     e0 = create_rock(0,mass=1e6)
#     e1 = create_rock(1,mass=1e6,position=(1e3,0))

#     elist = [e0,e1]
#     edict = {0:e0,1:e1}

#     sys = GravitySystem()
#     sys.update(elist,edict)
    
#     print(e0.get(Forces).components["Gravity"])

#     assert e0.get(Forces).components["Gravity"][0]-66.743<0.01 and e1.get(Forces).components["Gravity"][0]+66.743<0.01




# Need to test collision system

# Thruster and other systems will probably change before the tests matter

# Render will not be a system soon, and will need a different testing thing
