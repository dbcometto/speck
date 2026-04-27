"""Inspector window for an entity"""
import pyglet

from ..windows import SpeckWindow
from ...core import World
from ...utils import _hex_to_rgb
from ...config import SELECTED_COLOR, OTHER_COLOR, GRAY_COLOR, DARK_GRAY_COLOR, MAX_INSPECTOR_COL_WIDTH, MIN_INSPECTOR_COL_WIDTH
from .widgets import ComponentInspectorWidget, TextWidget
from ...components.functional import Identity, Surface, SurfacePosition
from ...components.dynamics import Position,Velocity,Acceleration,Attitude,AngularVelocity,AngularAcceleration,Mass
from ...components.assemblies import Assembly

class InspectorWindow(SpeckWindow):
    def __init__(self, world, windows, eid, width=350, height=500) -> None:
        super().__init__(world, windows, width, height)
        self.eid = eid
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
            width=width, height=height - 45,
            world=world, eid=eid,
            order=[Identity, 
                   Mass, 
                   Surface, 
                   Position, 
                   SurfacePosition, 
                   Velocity, 
                   Acceleration, 
                   Attitude, 
                   AngularVelocity, 
                   AngularAcceleration, 
                   Assembly]
        )

    def on_draw(self) -> None:
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
        self._inspector.width = width
        self._inspector.height = height - 45
        self._inspector._on_reposition()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y) -> None:
        self._inspector.on_mouse_scroll(x, y, scroll_x, scroll_y)