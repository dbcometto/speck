# Tests for entities

from speck.entities import Entity
from speck.components import Position, Velocity

def test_entity_creation():
    """Test init entity"""
    e = Entity(0)
    assert e.id==0 and e.components == {}

def test_entity_addAndGetComponent():
    """Test add and get component"""
    e = Entity(0)
    e.add_component(Position(x=0,y=0))

    pos = e.get(Position)

    assert pos.x == 0 and pos.y == 0

def test_entity_removeComponent():
    """Test remove component"""
    e = Entity(0)
    e.add_component(Position(x=0,y=0))
    e.remove_component(Position)
    assert e.get(Position) is None

def test_entity_has():
    """Test has"""
    e = Entity(0)
    e.add_component(Position(x=0,y=0))
    assert e.has(Position) and not e.has(Velocity)

def test_entity_todict():
    """Test todict"""
    e = Entity(0)
    e.add_component(Position(x=0,y=0))
    assert e.to_dict() == {"id": 0, "components": {"Position" : {"x": 0, "y": 0} }}

def test_entity_fromdict():
    """Test fromdict"""
    e = Entity.from_dict({"id": 0, "components": {"Position" : {"x": 0, "y": 0} }})
    pos = e.get(Position)
    assert pos.x==0 and pos.y==0