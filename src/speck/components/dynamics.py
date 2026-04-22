"""Establish dynamics components"""
from typing import Self

from .component import Component


# Movement 

class Position(Component):
    """A position component"""
    units = {"x": "km", "y": "km", "z": "km"}

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """Give an entity position in km"""
        self.x = x
        self.y = y
        self.z = z

class Velocity(Component):
    """A velocity component"""
    units = {"x": "km/s", "y": "km/s", "z": "km/s"}

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """Give an entity velocity in km/s"""
        self.x = x
        self.y = y
        self.z = z

class Acceleration(Component):
    """An acceleration component"""
    units = {"x": "km/s^2", "y": "km/s^2", "z": "km/s^2"}

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """Give an entity acceleration in km/s^2"""
        self.x = x
        self.y = y
        self.z = z




# Mass

class Mass(Component):
    """A mass component"""
    units = {"mass": "kg"}
    
    def __init__(self, mass: float = 0.0) -> None:
        """Give an entity mass in kg"""
        self.mass = mass





# Gravity

class GravitySource(Component):
    """This entity creates gravity"""
    def __init__(self) -> None:
        """Make this entity create gravity"""
        pass

class GravityConsumer(Component):
    """That entity experiences gravity"""
    def __init__(self) -> None:
        """Make this entity experience gravity"""
        pass