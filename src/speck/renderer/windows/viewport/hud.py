"""Owns the HUD"""
import pyglet

from ....core.world import World
from .camera import Camera
from .input_handler import InputHandler
from ....config import SELECTED_COLOR, OTHER_COLOR, KEYBINDS

class HUD():
    """The HUD"""
    def __init__(self, world: World, camera: Camera, input_handler: InputHandler, width: int = 800, height: int = 600) -> None:
        """Init the HUD"""
        self.world = world
        self.camera = camera
        self.width = width
        self.height = height
        self.input_handler = input_handler

        self.show_debug = True
        self.show_scale = True
        self.show_grid = False

        self.cursor_screen_x = 0.0
        self.cursor_screen_y = 0.0
        self.cursor_world_x = 0.0
        self.cursor_world_y = 0.0

        self.debug_offset = 20 # from top
        self.timewarp_offset = 20 # From bottom

        self._batch = pyglet.graphics.Batch()
        self._debug_label = pyglet.text.Label(
            text="",
            x=10,
            y=height - self.debug_offset,
            font_name="consolas",
            font_size=11,
            color=(200, 200, 200, 255),
            batch=self._batch
        )

        self._fps = -1.0
        self._ups = -1.0



        # Buttons
        self._button_labels = {}
        self._button_regions = {}
        self._button_actions = {}
        self._button_active = {}  # name -> callable that returns bool for highlight

        # Add timewarp buttons
        timewarps = {"P": 0, "1s/s": 1, "1min/s": 60, "1hr/s": 3600, "1d/s": 86400}
        x = 10
        y = self.timewarp_offset
        for name, value in timewarps.items():
            self._add_button(
                name=name,
                text=name,
                x=x, y=y, width=40,
                action=lambda v=value: setattr(self.world, 'timewarp', v),
                active=lambda v=value: self.world.timewarp == v
            )
            x += 50 

    def _add_button(self, name: str, text: str, x: int, y: int, width: int, 
                   action, active=None) -> None:
        """Add a button to the HUD"""
        self._button_labels[name] = pyglet.text.Label(
            text=text,
            x=x, y=y,
            font_name="Consolas",
            font_size=11,
            color=(200, 200, 200, 255),
            batch=self._batch
        )
        self._button_regions[name] = (x, y - 5, x + width, y + 15) # TODO: magic numbers
        self._button_actions[name] = action
        self._button_active[name] = active

    def update_ups(self, dt: float) -> None:
        self._ups = 1.0 / dt if dt > 0 else 0.0

    def update_fps(self, dt: float) -> None:
        self._fps = 1.0 / dt if dt > 0 else 0.0
    


    # Draw (called by renderer)
    def draw(self) -> None:
        """Draw the HUD"""
        if self.show_debug: 
            self._debug_label.text = (
                f"t={self.world.time:.1f}s  "
                f"twarp={self.world.timewarp:.1f}x  "
                f"sub_dt={self.world.last_sub_dt:.1f}s  "
                f"sub_steps={self.world.last_sub_steps:<4d}  "
                f"ups={self._ups:.0f}  "
                f"fps={self._fps:.0f}  "
                f"cursor=({self.cursor_world_x:.1f}, {self.cursor_world_y:.1f})"
                f"select={self.input_handler.selected_eid}"
                f"hover={self.input_handler.hover_eid}"
                f"follow={self.input_handler.follow_eid}"
            )
        else:
            self._debug_label.text = ""

        # Update button highlight colors
        for name, label in self._button_labels.items():
            active_fn = self._button_active.get(name)
            if active_fn and active_fn():
                label.color = self._hex_to_rgb(SELECTED_COLOR)
            else:
                label.color = self._hex_to_rgb(OTHER_COLOR)

        self._batch.draw()

    # Pyglet Handlers
    def on_mouse_motion(self, x, y, dx, dy):
        self.cursor_screen_x = x
        self.cursor_screen_y = y
        self.cursor_world_x, self.cursor_world_y = self.camera.screen_to_world(self.cursor_screen_x, self.cursor_screen_y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cursor_screen_x = x
        self.cursor_screen_y = y
        self.cursor_world_x, self.cursor_world_y = self.camera.screen_to_world(self.cursor_screen_x, self.cursor_screen_y)

    def on_resize(self, width, height):
        self.width = width
        self.height = height
        self._debug_label.y = height - self.debug_offset
        
        # Reposition timewarp buttons
        x = 10 # TODO: magic
        y = self.timewarp_offset
        for name in self._button_labels:
            self._button_labels[name].x = x
            self._button_labels[name].y = y
            old_region = self._button_regions[name]
            w = old_region[2] - old_region[0]  # preserve original width
            self._button_regions[name] = (x, y - 4, x + w, y + 15) # TODO: magic
            x += 50

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        for name, (x1, y1, x2, y2) in self._button_regions.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                self._button_actions[name]()

    def on_key_press(self, symbol, modifiers) -> None:
        handled = False

        if symbol in KEYBINDS["toggle_debug_hud"]:
            self.show_debug = not self.show_debug
            handled = True

        return handled


    
    # Helpers

    def _hex_to_rgb(self, hex: str) -> tuple[int, int, int]:
        "Convert hex string to RGB"
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))