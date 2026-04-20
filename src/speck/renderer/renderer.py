"""Render the world"""
from abc import ABC, abstractmethod
from enum import IntEnum

from ..core import World
from .camera import Camera
from .hud import HUD

# Rendering
class RenderType(IntEnum):
    POINT = 0
    CIRCLE = 1

class Renderer(ABC):
    """A base renderer"""
    def __init__(self, world: World, camera: Camera, hud: HUD, width: int = 800, height: int = 600):
        """Establish a renderer"""
        self.world = world
        self.camera = camera
        self.width = width
        self.height = height
        self.hud = hud

    @abstractmethod
    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Calculate the screen position given world position"""
        ...
    
    @abstractmethod
    def on_draw(self):
        """Handler for draw event"""
        ...