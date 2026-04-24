"""A collection of functional components"""
from .component import Component

# Name and Type

class Identity(Component):
    """Give an entity a human-readable identity"""
    def __init__(self, name: str = "", classification: str = "unclassified", subtype: str = "") -> None:
        """Give an entity a human-readable identity"""
        self.name = name
        self.classification = classification
        self.subtype = subtype






# Surfaces

class Surface(Component):
    """Give an entity a surface map"""
    def __init__(self, width: float, height: float):
        """Give an entity a surface map"""
        self.width = width   # km
        self.height = height # km
        # TODO: useful data

class SurfacePosition(Component):
    """Give an entity a position on a surface"""
    def __init__(self, body_eid: int, x: float = 0.0, y: float = 0.0):
        """Give an entity a position on a surface"""
        self.body_eid = body_eid
        self.x = x  # km from origin
        self.y = y  # km from origin