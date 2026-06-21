"""The assembly flowgraph editor"""
import pyglet

from ..windows import SpeckWindow
from ...utils import _hex_to_rgb
from ...config import DARK_GRAY_COLOR, SELECTED_COLOR, OTHER_COLOR, GRAY_COLOR, KEYBINDS
from .widgets import FlowgraphCanvasWidget, TextWidget


class FlowgraphWindow(SpeckWindow):
    TITLE_PADDING = 35

    def __init__(self, request_conn, windows: list, assembly_eid: int,
                 width: int = 700, height: int = 500) -> None:
        super().__init__(windows, width, height)
        self.assembly_eid = assembly_eid
        self.request_conn = request_conn
        self.window.set_caption(f"Speck Flowgraph: Entity {assembly_eid}")
        pyglet.gl.glClearColor(*_hex_to_rgb(DARK_GRAY_COLOR, return_as_floats=True))
        self.window.push_handlers(self)

        self._canvas = FlowgraphCanvasWidget(
            0, 0, width, height,
            on_inspect=lambda eid: self._open_inspector(eid)
        )

        self._title = TextWidget(
            x=8, y=height - self.TITLE_PADDING,
            width=300, height=20,
            text=f"Entity {assembly_eid}",
            font_size=12,
            color=SELECTED_COLOR,
            background_alpha=0,
            anchor_top=True, anchor_left=True
        )

        # Request initial data
        self._request_data()

    def _request_data(self) -> None:
        try:
            self.request_conn.send(("assembly", self.assembly_eid))
        except Exception:
            pass

    def set_data(self, data: dict | None) -> None:
        if data is None:
            return
        self._title._text = data.get("name", f"Entity {self.assembly_eid}")
        self._canvas.load_from_data(data)

    def _open_inspector(self, eid: int | None) -> None:
        if eid is None:
            return
        from ...renderer.windows.inspector import InspectorWindow
        for w in self.windows:
            if isinstance(w, InspectorWindow) and w.eid == eid:
                w.window.activate()
                return
        InspectorWindow(self.request_conn, self.windows, eid)

    def on_draw(self):
        self.window.clear()
        batch = pyglet.graphics.Batch()
        self._canvas.draw(batch)
        self._title.draw(batch)
        batch.draw()

    def on_resize(self, width, height):
        self.width  = width
        self.height = height
        self._canvas.width  = width
        self._canvas.height = height
        self._title.on_resize(width, height)

    def on_mouse_press(self, x, y, button, modifiers):
        self._canvas.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self._canvas.on_mouse_release(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._canvas.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self._canvas.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_motion(self, x, y, dx, dy):
        self._canvas.on_mouse_motion(x, y, dx, dy)

    def on_close(self):
        super().on_close()

    def on_key_press(self, symbol, modifiers) -> None:
        if symbol in KEYBINDS["inspect"] and self._canvas._selected:
            self._open_inspector(self._canvas._selected.part_eid)