"""Render the world using Pyglet"""
import pyglet
import time
import math

from .camera import Camera
from .hud import HUD
from .input_handler import InputHandler
from ...windows import SpeckWindow
from ....config import POINT_ICON_RADIUS, MIN_BODY_SCREEN_RADIUS, SELECT_SQUARE_PADDING
from ....config import SELECTED_COLOR, OTHER_COLOR, BACKGROUND_COLOR, VELOCITY_ARROW_COLOR
from ....config import GRID_TARGET_PX, GRID_MAX_LINES, GRID_MAJOR_COLOR, GRID_MINOR_COLOR, SCALE_BAR_TARGET_PX, TIMEWARP_PANEL_WIDTH
from ....components.rendering import RenderType
from ....utils import _hex_to_rgb


class ViewportWindow(SpeckWindow):
    """A 2D renderer using Pyglet"""
    def __init__(self, snapshot_queue, request_conn, command_queue,
                 windows: list, width: int = 800, height: int = 600):
        super().__init__(windows, width, height)
        self.snapshot_queue = snapshot_queue
        self.request_conn   = request_conn
        self.command_queue  = command_queue
        self._snapshot      = {"entities": {}, "time": 0, "timewarp": 1,
                                "last_sub_dt": 0, "last_sub_steps": 0}

        self.camera        = Camera(width, height)
        self.input_handler = InputHandler(self.camera, self.windows, self.command_queue, self.request_conn)
        self.hud           = HUD(self.camera, self.input_handler, self.command_queue, width, height)
        self._last_draw    = time.perf_counter()

        pyglet.gl.glClearColor(*_hex_to_rgb(BACKGROUND_COLOR, return_as_floats=True))
        self.window.push_handlers(self)
        self.window.push_handlers(self.camera)
        self.window.push_handlers(self.input_handler)
        self.window.push_handlers(self.input_handler.keys)
        self.window.push_handlers(self.hud)

    def set_snapshot(self, snapshot: dict) -> None:
        self._snapshot = snapshot
        self.input_handler._snapshot_entities = snapshot.get("entities", {})
        self.input_handler._current_timewarp  = snapshot.get("timewarp", 1.0)
        self.hud.set_snapshot(snapshot)

    def on_draw(self):
        now = time.perf_counter()
        dt  = now - self._last_draw
        self._last_draw = now
        self.hud.update_fps(dt)
        self.input_handler._update_camera_keys(dt)

        self._update_follow()

        self.window.clear()
        batch  = pyglet.graphics.Batch()
        shapes = []

        self._draw_grid(batch, shapes)

        entities = self._snapshot.get("entities", {})
        for eid, e in entities.items():
            sx, sy = self.camera.world_to_screen(e["x"], e["y"])

            render_type = e["render_type"]
            color       = SELECTED_COLOR if eid == self.input_handler.selected_eid else OTHER_COLOR
            tuple_color = _hex_to_rgb(color)

            if render_type == RenderType.POINT:
                if sx < 0 or sx > self.width or sy < 0 or sy > self.height:
                    continue
                shapes.append(pyglet.shapes.Circle(
                    x=sx, y=sy, radius=POINT_ICON_RADIUS,
                    color=tuple_color, batch=batch))

            elif render_type == RenderType.CIRCLE:
                radius = max((e["radius"] or 1.0) * self.camera.zoom, MIN_BODY_SCREEN_RADIUS)
                if sx + radius < 0 or sx - radius > self.width or \
                   sy + radius < 0 or sy - radius > self.height:
                    continue
                shapes.append(pyglet.shapes.Circle(
                    x=sx, y=sy, radius=radius,
                    color=tuple_color, batch=batch))

            elif render_type == RenderType.TRIANGLE:
                if sx < 0 or sx > self.width or sy < 0 or sy > self.height:
                    continue
                r = POINT_ICON_RADIUS * 1.5
                shapes.append(pyglet.shapes.Triangle(
                    sx,           sy + r,
                    sx - r*0.866, sy - r*0.5,
                    sx + r*0.866, sy - r*0.5,
                    color=tuple_color, batch=batch))

                vx, vy = e.get("vx", 0.0), e.get("vy", 0.0)
                speed = math.sqrt(vx**2 + vy**2)
                if speed > 0.01:
                    direction = math.atan2(vy, vx)
                    vr = speed * 2.0
                    end_x = sx + vr * math.cos(direction)
                    end_y = sy + vr * math.sin(direction)
                    shapes.append(pyglet.shapes.Line(
                        sx, sy, end_x, end_y,
                        color=_hex_to_rgb(VELOCITY_ARROW_COLOR), batch=batch))

            # Hover square
            if eid == self.input_handler.hover_eid:
                if render_type == int(RenderType.CIRCLE):
                    size = 2 * radius + SELECT_SQUARE_PADDING
                else:
                    size = 2 * POINT_ICON_RADIUS + SELECT_SQUARE_PADDING
                shapes.append(pyglet.shapes.Box(
                    x=sx - size/2, y=sy - size/2,
                    width=size, height=size,
                    color=_hex_to_rgb(SELECTED_COLOR), batch=batch))
                
        
        self._draw_scale_bar(batch, shapes)

        batch.draw()

        
        self.hud.draw()

        # Handle any pending inspector/assembly responses
        self._handle_responses()

    def on_resize(self, width, height):
        self.width  = width
        self.height = height

    def on_close(self):
        super().on_close()
        viewers = [v for v in self.windows if isinstance(v, ViewportWindow)]
        if len(viewers) < 1:
            pyglet.app.exit()

    def _update_follow(self) -> None:
        if self.input_handler.follow_eid is not None:
            e = self._snapshot.get("entities", {}).get(self.input_handler.follow_eid)
            if e:
                self.camera.origin_x = e["x"]
                self.camera.origin_y = e["y"]

    def _handle_responses(self) -> None:
        """Check for pending inspector/assembly responses from sim"""
        if not self.request_conn.poll():
            return
        try:
            msg = self.request_conn.recv()
        except Exception:
            return

        if msg[0] == "entity":
            eid, data = msg[1], msg[2]
            from ....renderer.windows.inspector import InspectorWindow
            for w in self.windows:
                if isinstance(w, InspectorWindow) and w.eid == eid:
                    w.set_data(data)
                    return

        elif msg[0] == "assembly":
            eid, data = msg[1], msg[2]
            from ....renderer.windows.flowgraph import FlowgraphWindow
            for w in self.windows:
                if isinstance(w, FlowgraphWindow) and w.assembly_eid == eid:
                    w.set_data(data)
                    return

    def _draw_grid(self, batch, shapes) -> None:
        raw_spacing = GRID_TARGET_PX / self.camera.zoom
        exp = math.floor(math.log10(raw_spacing))
        spacing_coarse = 10 ** exp
        spacing_fine   = 10 ** (exp - 1)

        x0, y0 = self.camera.screen_to_world(0, 0)
        x1, y1 = self.camera.screen_to_world(self.width, self.height)
        left, right  = min(x0, x1), max(x0, x1)
        bottom, top  = min(y0, y1), max(y0, y1)

        if (right - left) / spacing_fine <= GRID_MAX_LINES:
            for spacing, color in [
                (spacing_fine,   _hex_to_rgb(GRID_MINOR_COLOR)),
                (spacing_coarse, _hex_to_rgb(GRID_MAJOR_COLOR))
            ]:
                x = math.floor(left / spacing) * spacing
                while x <= right + spacing:
                    sx, _ = self.camera.world_to_screen(x, 0)
                    shapes.append(pyglet.shapes.Line(
                        sx, 0, sx, self.height, color=color, batch=batch))
                    x += spacing

                y = math.floor(bottom / spacing) * spacing
                while y <= top + spacing:
                    _, sy = self.camera.world_to_screen(0, y)
                    shapes.append(pyglet.shapes.Line(
                        0, sy, self.width, sy, color=color, batch=batch))
                    y += spacing

    def _draw_scale_bar(self, batch, shapes) -> None:
        target_px = 150
        world_len = target_px / self.camera.zoom

        exp = math.floor(math.log10(world_len))
        candidates = [10**exp, 2*10**exp, 5*10**exp]
        world_snap = min(candidates, key=lambda v: abs(v - world_len))
        bar_px = world_snap * self.camera.zoom

        # anchor to left of timewarp panel
        margin_right = TIMEWARP_PANEL_WIDTH + 10 + 20
        bar_x = self.width - margin_right - bar_px
        bar_y = 18
        bar_h = 4

        shapes.append(pyglet.shapes.Rectangle(
            x=bar_x, y=bar_y,
            width=bar_px, height=bar_h,
            color=_hex_to_rgb(OTHER_COLOR), batch=batch
        ))
        shapes.append(pyglet.shapes.Rectangle(
            x=bar_x, y=bar_y - 4,
            width=2, height=bar_h + 8,
            color=_hex_to_rgb(OTHER_COLOR), batch=batch
        ))
        shapes.append(pyglet.shapes.Rectangle(
            x=bar_x + bar_px - 2, y=bar_y - 4,
            width=2, height=bar_h + 8,
            color=_hex_to_rgb(OTHER_COLOR), batch=batch
        ))

        if world_snap >= 1000:
            label = f"{world_snap/1000:.0f} Mm"
        elif world_snap >= 1:
            label = f"{world_snap:.0f} km"
        else:
            label = f"{world_snap*1000:.0f} m"

        shapes.append(pyglet.text.Label(
            text=label,
            x=bar_x + bar_px / 2, y=bar_y + 10,
            font_name="Consolas", font_size=10,
            color=_hex_to_rgb(OTHER_COLOR),
            anchor_x="center",
            batch=batch
        ))