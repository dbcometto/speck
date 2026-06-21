"""An input handler"""
import pyglet
import math
from typing import Callable

from ....core import World
from ....components.dynamics import Position
from .camera import Camera
from ....config import SELECTION_TOLERANCE, KEYBINDS, ZOOM_FACTOR, CAMERA_SENSITIVITY, TIMEWARP_PRESETS

class InputHandler():
    """An input handler"""
    def __init__(self, camera: Camera, windows: list, command_queue, request_conn):
        """Init an input handler"""
        self.camera = camera
        self.windows = windows
        self.command_queue = command_queue
        self.request_conn = request_conn

        self._snapshot_entities = {}  # latest snapshot entities, set externally
        self._current_timewarp = 1.0  # updated from snapshot externally

        self._is_dragging = False
        self._drag_start = (0, 0)

        self.selected_eid: int | None = None
        self.follow_eid: int | None = None
        self.hover_eid: int | None = None

        self.is_following = False


        self.keys = pyglet.window.key.KeyStateHandler()
        self.old_timewarp = None

    def set_minimap_follow(self, on_minimap_follow: Callable) -> None:
        """Allow the keybinding for minimap following to work"""
        self.on_minimap_follow = on_minimap_follow


    def open_inspector(self, eid: int | None) -> None:
        if eid is not None:
            from ....renderer.windows.inspector import InspectorWindow
            for w in self.windows:
                if isinstance(w, InspectorWindow) and w.eid == eid:
                    w.window.activate()
                    return
            InspectorWindow(self.request_conn, self.windows, eid)

    def open_graph(self, eid: int | None) -> None:
        if eid is not None:
            from ....renderer.windows.flowgraph import FlowgraphWindow
            for w in self.windows:
                if isinstance(w, FlowgraphWindow) and w.assembly_eid == eid:
                    w.window.activate()
                    return
            FlowgraphWindow(self.request_conn, self.windows, eid)



    def set_follower(self, eid: int | None) -> None:
        """Set the camera for a new follower or reset the origin"""
        if eid is not None:
            if eid in self._snapshot_entities:
                e = self._snapshot_entities[eid]
                self.follow_eid = eid
                old_origin_x = self.camera.origin_x
                old_origin_y = self.camera.origin_y
                self.camera.origin_x = e["x"]
                self.camera.origin_y = e["y"]
                self.camera.x = self.camera.x - e["x"] + old_origin_x
                self.camera.y = self.camera.y - e["y"] + old_origin_y
            self.is_following = True
        else:
            self.follow_eid = None
            self.camera.x = self.camera.x + self.camera.origin_x
            self.camera.y = self.camera.y + self.camera.origin_y
            self.camera.origin_x = 0.0
            self.camera.origin_y = 0.0
            self.is_following = False


    def timewarp_up(self) -> None:
        for v in TIMEWARP_PRESETS:
            if v > self._current_timewarp:
                self.command_queue.put(("timewarp", v))
                return

    def timewarp_down(self) -> None:
        for v in reversed(TIMEWARP_PRESETS):
            if v < self._current_timewarp:
                self.command_queue.put(("timewarp", v))
                return


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
        self.camera.zoom *= ZOOM_FACTOR if scroll_y > 0 else 1 / ZOOM_FACTOR

    def _on_click(self, x, y) -> None:
        wx, wy = self.camera.screen_to_world(x, y)
        self.selected_eid = self._pick_entity(wx, wy)
    
    def _pick_entity(self, wx, wy) -> int | None:
        closest_eid = None
        closest_dist = float('inf')

        for eid, e in self._snapshot_entities.items():
            d = math.sqrt((e["x"] - wx)**2 + (e["y"] - wy)**2)
            if d < closest_dist:
                closest_dist = d
                closest_eid = eid

        tolerance = SELECTION_TOLERANCE / self.camera.zoom
        return closest_eid if closest_dist < tolerance else None
    
    def on_mouse_motion(self, x, y, dx, dy) -> None:
        self.hover_eid = self._pick_entity(*self.camera.screen_to_world(x, y))

    def _update_camera_keys(self, dt: float) -> None:
        handled = False
        speed = CAMERA_SENSITIVITY / self.camera.zoom

        for key in KEYBINDS["move_up"]:
            if self.keys[key]:
                self.camera.y += speed * dt
                handled = True

        for key in KEYBINDS["move_down"]:
            if self.keys[key]:
                self.camera.y -= speed * dt
                handled = True

        for key in KEYBINDS["move_left"]:
            if self.keys[key]:
                self.camera.x -= speed * dt
                handled = True

        for key in KEYBINDS["move_right"]:
            if self.keys[key]:
                self.camera.x += speed * dt
                handled = True

        return handled

    def on_key_press(self, symbol, modifiers) -> None:
        handled = False



        # Entity Interactions
        if symbol in KEYBINDS["follow"]:
            if not self.is_following or self.is_following and self.selected_eid != self.follow_eid:
                self.set_follower(self.selected_eid)
            else:
                self.set_follower(None)

            handled = True

        if symbol in KEYBINDS["unfollow"]:
            self.set_follower(None)
            handled = True

        if symbol in KEYBINDS["deselect"]:
            self.selected_eid = None
            handled = True

        if symbol in KEYBINDS["inspect"]:
            self.open_inspector(self.selected_eid)
            handled = True

        if symbol in KEYBINDS["focus_minimap"]:
            self.on_minimap_follow(self.selected_eid)
            handled = True
        
        if symbol in KEYBINDS["open_graph"]:
            self.open_graph(self.selected_eid)
            handled = True


        # Time
        if symbol in KEYBINDS["pause"]:
            if self._current_timewarp == 0.0:
                if self.old_timewarp is not None:
                    self.command_queue.put(("timewarp", self.old_timewarp))
                    self.old_timewarp = None
                else:
                    self.command_queue.put(("timewarp", 1.0))
            else:
                self.old_timewarp = self._current_timewarp
                self.command_queue.put(("timewarp", 0.0))
            handled = True

        if symbol in KEYBINDS["increase_timewarp"]:
            self.timewarp_up()
            handled = True

        if symbol in KEYBINDS["decrease_timewarp"]:
            self.timewarp_down()
            handled = True

        

        
    
        return handled
        





    
            