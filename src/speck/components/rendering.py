"""Rendering components"""

from .component import Component
from ..renderer import RenderType

def hex_to_rgb(hex: str) -> tuple[int, int, int]:
        "Convert hex string to RGB"
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))


class RenderData(Component):
    """Contains rendering data"""
    def __init__(self, render_type: int = RenderType.POINT, color = "#FFFFFF", radius = 1.0):
        """Render this entity"""
        self.render_type = render_type
        
        if isinstance(color, str):
            color = hex_to_rgb(color)
        self.color = color

        self.radius = radius # used for RenderType.CIRCLE

    
            


