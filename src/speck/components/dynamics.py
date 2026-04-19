"""Establish dynamics components"""
from typing import Self

from .component import Component

class Position(Component):
    """A position component"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> Self:
        """Create a position component"""
        self.x = x
        self.y = y
        self.z = z