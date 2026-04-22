"""Render the world using Pyglet"""
import pyglet
import time
from enum import IntEnum

from .camera import Camera
from .hud import HUD
from .input_handler import InputHandler
from ...windows import SpeckWindow
from ....core import World
from ....components.dynamics import Position
from ....components.rendering import RenderData, RenderType
from ....config import POINT_ICON_RADIUS, MIN_BODY_SCREEN_RADIUS, SELECT_SQUARE_PADDING
from ....config import SELECTED_COLOR, OTHER_COLOR, BACKGROUND_COLOR
from ....utils import _hex_to_rgb

class ViewportWindow(SpeckWindow):
    """A 2D renderer using Pyglet"""
    def __init__(self, world: World, windows: list[SpeckWindow], width: int = 800, height: int = 600):
        """Establish the Pyglet renderer"""
        super().__init__(world, windows, width, height) # creates window, hud, camera, and input handler
        self.camera = Camera(width, height)
        self.input_handler = InputHandler(world, self.camera, self.windows)
        self.hud = HUD(world, self.camera, self.input_handler, width, height)
        self._last_draw = time.perf_counter() 

        # Pyglet State
        pyglet.gl.glClearColor(*_hex_to_rgb(BACKGROUND_COLOR, return_as_floats=True))
        self.window.push_handlers(self)
        self.window.push_handlers(self.camera)
        self.window.push_handlers(self.input_handler)
        self.window.push_handlers(self.input_handler.keys)
        self.window.push_handlers(self.hud)
    
    def on_draw(self):
        """Handler for draw event"""
        now = time.perf_counter()
        dt = now - self._last_draw
        self._last_draw = now
        self.hud.update_fps(dt)
        self.input_handler._update_camera_keys(dt)

        self._update_follow()

        self.window.clear()
        batch = pyglet.graphics.Batch()
        shapes = []

        positions = self.world.get_component(Position)
        renderdatas = self.world.get_component(RenderData)

        for eid in positions.keys() & renderdatas.keys():
            pos = positions[eid]
            sx, sy = self.camera.world_to_screen(pos.x, pos.y)

            data = renderdatas[eid]
            color = SELECTED_COLOR if eid == self.input_handler.selected_eid else OTHER_COLOR
            tuple_color = _hex_to_rgb(color)

            if data.render_type == RenderType.POINT:
                if sx < 0 or sx > self.width or sy < 0 or sy > self.height:
                    continue

                shapes.append(pyglet.shapes.Circle(x=sx, y=sy, radius=POINT_ICON_RADIUS, color=tuple_color, batch=batch))

            elif data.render_type == RenderType.CIRCLE:
                radius = max(data.radius*self.camera.zoom,MIN_BODY_SCREEN_RADIUS)

                if sx + radius < 0 or sx - radius > self.width or sy + radius < 0 or sy - radius > self.height:
                    continue

                shapes.append(pyglet.shapes.Circle(x=sx, y=sy, radius=radius, color=tuple_color, batch=batch))


            # Draw hover square
            if eid == self.input_handler.hover_eid:
                if data.render_type == RenderType.POINT:
                    size = 2*POINT_ICON_RADIUS + SELECT_SQUARE_PADDING
                
                elif data.render_type == RenderType.CIRCLE:
                    size = 2*radius + SELECT_SQUARE_PADDING
                
                shapes.append(pyglet.shapes.Box(
                    x=sx - size/2, 
                    y=sy - size/2, 
                    width=size, 
                    height=size, 
                    color=_hex_to_rgb(SELECTED_COLOR),
                    batch=batch
                ))

        batch.draw()
        self.hud.draw()


    def on_resize(self, width, height):
        self.width = width
        self.height = height


    def on_close(self):
        super().on_close()

        viewers = [v for v in self.windows if isinstance(v,ViewportWindow)]
        if len(viewers) < 1:
            pyglet.app.exit()



    # Helpers

    def _update_follow(self) -> None:
        """Make the camera track an entity"""
        if self.input_handler.follow_eid is not None:
            positions = self.world.get_component(Position)
            if self.input_handler.follow_eid in positions:
                pos = positions[self.input_handler.follow_eid]

                self.camera.origin_x = pos.x
                self.camera.origin_y = pos.y
