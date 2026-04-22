"""Owns the HUD"""
import pyglet

from ....core.world import World
from .camera import Camera
from .input_handler import InputHandler
from ....config import SELECTED_COLOR, OTHER_COLOR, KEYBINDS
from ....utils import _hex_to_rgb
from .widget import Widget, TextWidget, TextButtonWidget, PanelWidget, SelectionPanelWidget, ActionBarWidget

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
        # self.show_scale = True # TODO
        # self.show_grid = False

        self.cursor_screen_x = 0.0
        self.cursor_screen_y = 0.0
        self.cursor_world_x = 0.0
        self.cursor_world_y = 0.0

        self.debug_offset = 20 # from top
        self.timewarp_offset = 20 # From bottom

        self._fps = -1.0
        self._ups = -1.0


        # Debug Panel
        self._widgets: list[Widget] = []

        # Debug text
        self._debug = TextWidget(
            x=10, y=height - 20,
            width=width, height=20,
            text=lambda: " ".join([
                f"t={self.world.time:.1f}s",
                f"twarp={self.world.timewarp:.1f}x",
                f"sub_dt={self.world.last_sub_dt:.1f}s",
                f"sub_steps={self.world.last_sub_steps:<4d}",
                "\n",
                f"ups={self._ups:.0f}",
                f"fps={self._fps:.0f}",
                "\n",
                f"cursor=({self.cursor_world_x:.1f}, {self.cursor_world_y:.1f})",
                f"select={self.input_handler.selected_eid}",
                f"hover={self.input_handler.hover_eid}",
                f"follow={self.input_handler.follow_eid}",
            ]) if self.show_debug else "",
            anchor_top = True, anchor_left = True,
            background_alpha=0
        )
        self._widgets.append(self._debug)



        # Timewarp buttons
        timewarps = {"  ||": 0, "1s/s": 1, "1min/s": 60, "1hr/s": 3600, "1d/s": 86400}

        width_per_button = 50
        gap_per_button = 5

        timewarp_panel = PanelWidget(
            x=0, y=10,  # x will be set by anchor
            width=width_per_button*len(timewarps)+gap_per_button*(len(timewarps)-1), 
            height=26,
            layout="horizontal", gap=gap_per_button, padding=0,
            anchor_bottom=True, anchor_right=True
        )
        timewarp_panel.x = width - timewarp_panel.width - 10
        for name, value in timewarps.items():
            timewarp_panel.add(TextButtonWidget(
                x=0, y=0,  # doesn't matter, layout overrides
                width=width_per_button, height=26,
                text=name,
                action=lambda v=value: setattr(self.world, 'timewarp', v),
                active=lambda v=value: self.world.timewarp == v,
            ))
        self._widgets.append(timewarp_panel)


        # Selection panel
        self._selection_panel = SelectionPanelWidget(self.world, self.input_handler, width, height)
        self._widgets.append(self._selection_panel)

        # Actions Panel
        self._action_bar = ActionBarWidget(self.world, self.input_handler, width, height)
        self._widgets.append(self._action_bar)





    def update_ups(self, dt: float) -> None:
        self._ups = 1.0 / dt if dt > 0 else 0.0

    def update_fps(self, dt: float) -> None:
        self._fps = 1.0 / dt if dt > 0 else 0.0
    


    # Draw (called by renderer)
    def draw(self) -> None:
        """Draw the HUD"""
        batch = pyglet.graphics.Batch()
        for w in self._widgets:
            if w.visible:
                w.draw(batch)
        batch.draw()



    # Pyglet Handlers
    def on_mouse_press(self, x, y, button, modifiers) -> bool:
        for w in reversed(self._widgets):
            if w.hit_test(x, y):
                w.on_mouse_press(x, y, button, modifiers)
                return True  # consumed regardless of widget action
        return False
            
    def on_mouse_release(self, x, y, button, modifiers) -> bool:
        for w in reversed(self._widgets):
            if w.hit_test(x, y):
                w.on_mouse_release(x, y, button, modifiers)
                return True
        return False
    
    def on_mouse_motion(self, x, y, dx, dy) -> None:
        self.cursor_world_x, self.cursor_world_y = self.camera.screen_to_world(x, y)
        for w in self._widgets:
            w.on_mouse_motion(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> None:
        self.cursor_world_x, self.cursor_world_y = self.camera.screen_to_world(x, y)

    def on_resize(self, width, height) -> None:
        self.width = width
        self.height = height
        for w in self._widgets:
            w.on_resize(width, height)

    def on_key_press(self, symbol, modifiers) -> bool:
        if symbol in KEYBINDS["toggle_debug_hud"]:
            self.show_debug = not self.show_debug
            return True
        return False









