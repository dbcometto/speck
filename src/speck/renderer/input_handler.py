"""An input handler"""
import pyglet
import math

from ..core import World
from ..components.dynamics import Position
from .camera import Camera
from ..config import SELECTION_TOLERANCE, KEYBINDS

class InputHandler():
    """An input handler"""
    def __init__(self, world: World, camera: Camera):
        """Init the input handler"""
        self.camera = camera
        self.world = world

        self._zoom_factor = 1.1
        self._is_dragging = False
        self._drag_start = (0,0)

        self.selected_eid: int | None = None
        self.follow_eid: int | None = None
        self.hover_eid: int | None = None



    # Pyglet Handlers

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        """Handler for mouse press"""
        if button == pyglet.window.mouse.LEFT:
            self._is_dragging = False

    def on_mouse_release(self, x, y, button, modifiers) -> None:
        """Handler for mouse release"""
        if button == pyglet.window.mouse.LEFT:
            if not self._is_dragging:
                self._on_click(x, y)
            self._is_dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> None:
        """Handler for mouse drag"""
        if buttons & pyglet.window.mouse.LEFT:
            self._is_dragging = True
            self.camera.x -= dx / self.camera.zoom
            self.camera.y -= dy / self.camera.zoom

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y) -> None:
        """Handler for mouse scroll"""
        self.camera.zoom *= self._zoom_factor if scroll_y > 0 else 1 / self._zoom_factor

    def _on_click(self, x, y) -> None:
        wx, wy = self.camera.screen_to_world(x, y)
        self.selected_eid = self._pick_entity(wx, wy)
    
    def _pick_entity(self, wx, wy) -> int | None:
        positions = self.world.get_component(Position)
        closest_eid = None
        closest_dist = float('inf')

        for eid, pos in positions.items():
            d = math.sqrt((pos.x - wx)**2 + (pos.y - wy)**2)
            if d < closest_dist:
                closest_dist = d
                closest_eid = eid

        tolerance = SELECTION_TOLERANCE / self.camera.zoom
        return closest_eid if closest_dist < tolerance else None
    
    def on_mouse_motion(self, x, y, dx, dy) -> None:
        self.hover_eid = self._pick_entity(*self.camera.screen_to_world(x, y))



    def on_key_press(self, symbol, modifiers) -> None:
        handled = False

        if symbol in KEYBINDS["follow"]:
            if self.selected_eid is not None:
                self.follow_eid = self.selected_eid
                self._set_follower(self.follow_eid)
                handled = True

        if symbol in KEYBINDS["unfollow"]:
            self.follow_eid = None
            self._set_follower(None)
            handled = True

        if symbol in KEYBINDS["deselect"]:
            self.selected_eid = None
            handled = True

        if handled:
            return True
        




    # Helpers

    def _set_follower(self, eid: int | None = None) -> None:
        """Set the camera for a new follower or reset the origin"""
        if eid is not None:
            positions = self.world.get_component(Position)
            if self.follow_eid in positions:
                pos = positions[eid]
                old_origin_x = self.camera.origin_x
                old_origin_y = self.camera.origin_y
                self.camera.origin_x = pos.x
                self.camera.origin_y = pos.y
                self.camera.x = self.camera.x - pos.x + old_origin_x
                self.camera.y = self.camera.y - pos.y + old_origin_y
        else:
            self.camera.x = self.camera.x + self.camera.origin_x
            self.camera.y = self.camera.y + self.camera.origin_y
            self.camera.origin_x = 0.0
            self.camera.origin_y = 0.0
            