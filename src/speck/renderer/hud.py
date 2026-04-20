"""Owns the HUD"""
import pyglet

from ..core.world import World
from .camera import Camera

class HUD():
    """The HUD"""
    def __init__(self, world: World, camera: Camera, width: int = 800, height: int = 600) -> None:
        """Init the HUD"""
        self.world = world
        self.camera = camera
        self.width = width
        self.height = height

        self.show_debug = True
        self.show_scale = True
        self.show_grid = False

        self.cursor_screen_x = 0
        self.cursor_screen_y = 0

        self._batch = pyglet.graphics.Batch()
        self._debug_label = pyglet.text.Label(
            text="",
            x=10,
            y=height - 20,
            font_name="consolas",
            font_size=11,
            color=(200, 200, 200, 255),
            batch=self._batch
        )

        self._fps = -1.0
        self._ups = -1.0

    def update_ups(self, dt: float) -> None:
        self._ups = 1.0 / dt if dt > 0 else 0.0

    def update_fps(self, dt: float) -> None:
        self._fps = 1.0 / dt if dt > 0 else 0.0

    def on_mouse_motion(self, x, y, dx, dy):
        self.cursor_screen_x = x
        self.cursor_screen_y = y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cursor_screen_x = x
        self.cursor_screen_y = y

    def _cursor_world_pos(self) -> tuple[float, float]:
        wx = (self.cursor_screen_x - self.width / 2) / self.camera.zoom + self.camera.x
        wy = (self.cursor_screen_y - self.height / 2) / self.camera.zoom + self.camera.y
        return wx, wy

    def draw(self) -> None:
        if self.show_debug:
            wx, wy = self._cursor_world_pos()
            self._debug_label.text = (
                f"t={self.world.time:.1f}s  "
                f"ups={self._ups:.0f}  "
                f"fps={self._fps:.0f}  "
                f"cursor=({wx:.1f}, {wy:.1f})"
            )
        self._batch.draw()