"""Inspector window for an entity"""
import pyglet
import time

from ..windows import SpeckWindow
from ...utils import _hex_to_rgb
from ...config import SELECTED_COLOR, OTHER_COLOR, GRAY_COLOR, DARK_GRAY_COLOR, MAX_INSPECTOR_COL_WIDTH, MIN_INSPECTOR_COL_WIDTH, INSPECTOR_REFRESH_PERIOD
from .widgets import ComponentInspectorWidget, TextWidget


class InspectorWindow(SpeckWindow):

    def __init__(self, request_conn, windows, eid, width=350, height=500) -> None:
        super().__init__(windows, width, height)
        self.eid          = eid
        self.request_conn = request_conn
        self._data        = {}  # latest component data from sim
        self._last_request_time = 0.0

        self.window.set_caption(f"Speck Inspector: Entity {eid}")
        pyglet.gl.glClearColor(*_hex_to_rgb(DARK_GRAY_COLOR, return_as_floats=True))
        self.window.push_handlers(self)

        self._batch = pyglet.graphics.Batch()

        self._title = TextWidget(
            x=10, y=height - 35,
            width=width, height=20,
            text=f"Entity {eid}",
            font_size=12,
            color=SELECTED_COLOR,
            background_alpha=0
        )

        self._inspector = ComponentInspectorWidget(
            x=10, y=0,
            width=width-10, height=height - 45,
            data={},
        )

        # Request initial data
        self._request_data()

    def _request_data(self) -> None:
        try:
            self.request_conn.send(("entity", self.eid))
        except Exception:
            pass

    def set_data(self, data: dict) -> None:
        self._data = data
        self._inspector.set_data(data)

    def on_draw(self) -> None:
        now = time.perf_counter()
        if now - self._last_request_time >= INSPECTOR_REFRESH_PERIOD:
            self._request_data()
            self._last_request_time = now

        self.window.clear()
        self._batch = pyglet.graphics.Batch()
        self._title.draw(self._batch)
        self._inspector.draw(self._batch)
        self._batch.draw()

    def on_resize(self, width, height) -> None:
        self.width = width
        self.height = height
        self._title.y = height - 35
        self._title.width = width
        self._title._on_reposition()
        self._inspector.width = width - 10
        self._inspector.height = height - 45
        self._inspector._on_reposition()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y) -> None:
        self._inspector.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        self._inspector.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers) -> None:
        self._inspector.on_mouse_release(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> None:
        self._inspector.on_mouse_drag(x, y, dx, dy, buttons, modifiers)