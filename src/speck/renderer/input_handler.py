"""An input handler"""
import pyglet
from .camera import Camera

class InputHandler():
    """An input handler"""
    def __init__(self, camera: Camera):
        """Init the input handler"""
        self.camera = camera
        self._zoom_factor = 1.1
        self._is_dragging = False
        self._drag_start = (0,0)

    def on_mouse_press(self, x, y, button, modifiers):
        """Handler for mouse press"""
        if button == pyglet.window.mouse.LEFT:
            self._dragging = True
            self._drag_start = (x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        """Handler for mouse release"""
        if button == pyglet.window.mouse.LEFT:
            self._dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Handler for mouse drag"""
        if self._dragging:
            self.camera.x -= dx / self.camera.zoom
            self.camera.y -= dy / self.camera.zoom

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Handler for mouse scroll"""
        self.camera.zoom *= self._zoom_factor if scroll_y > 0 else 1 / self._zoom_factor