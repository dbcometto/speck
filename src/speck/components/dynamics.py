"""Establish dynamics components"""
from typing import Self

from .component import Component


# Standard 

class Position(Component):
    """A position component"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> Self:
        """Create a position component"""
        self.x = x
        self.y = y
        self.z = z

class Velocity(Component):
    """A velocity component"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> Self:
        self.x = x
        self.y = y
        self.z = z

class Acceleration(Component):
    """An acceleration component"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> Self:
        self.x = x
        self.y = y
        self.z = z




# Gravity

class GravitySource(Component):
    """This entity creates gravity"""
    pass

class GravityEffect(Component):
    """That entity feels gravity"""
    pass