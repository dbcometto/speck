"""Render the world using Pyglet"""
import pyglet
import time

from ..renderer import RenderType, Renderer, Camera, HUD
from ..core import World
from ..components.dynamics import Position
from ..components.rendering import RenderData
from ..config import POINT_ICON_RADIUS, MIN_BODY_SCREEN_RADIUS

class PygletRenderer2D(Renderer):
    """A 2D renderer using Pyglet"""
    def __init__(self, world: World, camera: Camera, hud: HUD, width: int = 800, height: int = 600):
        """Establish the Pyglet renderer"""
        super().__init__(world, camera, hud, width, height)
        self._last_draw = time.perf_counter()     

        # Pyglet State
        self.window = pyglet.window.Window(width=self.width, height=self.height, caption="Speck", resizable = True)
        pyglet.gl.glClearColor(0.05, 0.05, 0.05, 1.0)
        self.window.push_handlers(self)
        self.window.push_handlers(hud)

    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Calculate the screen position given world position"""
        sx = (x - self.camera.x) * self.camera.zoom + self.width / 2
        sy = (y - self.camera.y) * self.camera.zoom + self.height / 2
        return sx, sy
    
    def on_draw(self):
        """Handler for draw event"""
        now = time.perf_counter()
        dt = now - self._last_draw
        self._last_draw = now
        self.hud.update_fps(dt)

        self.window.clear()
        batch = pyglet.graphics.Batch()
        shapes = []

        positions = self.world.get_component(Position)
        renderdatas = self.world.get_component(RenderData)

        for eid in positions.keys() & renderdatas.keys():
            pos = positions[eid]
            sx, sy = self.world_to_screen(pos.x, pos.y)

            data = renderdatas[eid]

            if data.render_type == RenderType.POINT:
                if sx < 0 or sx > self.width or sy < 0 or sy > self.height:
                    continue

                shapes.append(pyglet.shapes.Circle(x=sx, y=sy, radius=POINT_ICON_RADIUS, color=data.color, batch=batch))

            elif data.render_type == RenderType.CIRCLE:
                radius = max(data.radius*self.camera.zoom,MIN_BODY_SCREEN_RADIUS)

                if sx + radius < 0 or sx - radius > self.width or sy + radius < 0 or sy - radius > self.height:
                    continue

                shapes.append(pyglet.shapes.Circle(x=sx, y=sy, radius=radius, color=data.color, batch=batch))

        batch.draw()
        self.hud.draw()


    def on_resize(self, width, height):
        self.width = width
        self.height = height