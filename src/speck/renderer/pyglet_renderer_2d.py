"""Render the world using Pyglet"""
import pyglet

from .renderer import Renderer, Camera, InputHandler
from ..core import World
from ..components.dynamics import Position

class PygletRenderer2D(Renderer):
    """A 2D renderer using Pyglet"""
    def __init__(self, world: World, camera: Camera, width: int = 800, height: int = 600):
        """Establish the Pyglet renderer"""
        super().__init__(world, camera, width, height)     

        # Pyglet State
        self.window = pyglet.window.Window(width=self.width, height=self.height, caption="Speck")
        pyglet.gl.glClearColor(0.05, 0.05, 0.05, 1.0)
        self.window.push_handlers(self)

    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Calculate the screen position given world position"""
        sx = (x - self.camera.x) * self.camera.zoom + self.width / 2
        sy = (y - self.camera.y) * self.camera.zoom + self.height / 2
        return sx, sy
    
    def on_draw(self):
        """Handler for draw event"""
        self.window.clear()
        batch = pyglet.graphics.Batch()
        shapes = []

        positions = self.world.get(Position)
        # particles = self.world.get(RenderParticle)

        for eid, pos in positions.items():
            sx, sy = self.world_to_screen(pos.x, pos.y)

            # frustum cull
            if sx < 0 or sx > self.width or sy < 0 or sy > self.height:
                continue

            color = (255, 255, 255) # particles[eid].color if eid in particles else (255, 255, 255)
            shapes.append(pyglet.shapes.Circle(x=sx, y=sy, radius=3, color=color, batch=batch))

        batch.draw()