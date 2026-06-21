"""Render the world"""
from abc import ABC, abstractmethod
from typing import Self

import pyglet


class SpeckWindow(ABC):
    """A base renderer"""
    def __init__(self, windows: list[Self], width: int = 800, height: int = 600):
        """Establish a renderer"""
        self.window = pyglet.window.Window(width=width, height=height, caption="Speck", resizable=True)

        self.windows = windows
        self.windows.append(self)

        self.width = width
        self.height = height

    @abstractmethod
    def on_draw(self):
        """Handler for draw event"""
        ...

    def on_close(self):
        """Handler for closing event"""
        self.windows.remove(self)
        self.window.close()