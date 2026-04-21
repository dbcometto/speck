"""Render the world"""
from abc import ABC, abstractmethod
from typing import Self

import pyglet

from ...core import World
from ..camera import Camera
from ..hud import HUD
from ..input_handler import InputHandler

# Rendering
class SpeckWindow(ABC):
    """A base renderer"""
    def __init__(self, world: World, windows: list[Self], width: int = 800, height: int = 600):
        """Establish a renderer"""
        self.world = world
        self.window = pyglet.window.Window(width=width, height=height, caption="Speck", resizable = True)

        self.windows = windows
        self.windows.append(self)

        self.width = width
        self.height = height

        self.camera = Camera(width, height)
        self.hud = HUD(world, self.camera, width, height)
        self.input_handler = InputHandler(world, self.camera)
    

    @abstractmethod
    def on_draw(self):
        """Handler for draw event"""
        ...

    def on_close(self):
        """Handler for closing event"""
        self.windows.remove(self)
        self.window.close()