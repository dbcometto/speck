"""Rendering components"""
from enum import IntEnum

from .component import Component

class RenderType(IntEnum):
    POINT = 0
    CIRCLE = 1

class RenderData(Component):
    """Contains rendering data"""
    def __init__(self, render_type: int = RenderType.POINT, color: str = "#FFFFFF", radius: float | None = None):
        """Render this entity"""
        self.render_type = render_type
        self.color = color

        self.radius = radius # used for RenderType.CIRCLE

    
            


