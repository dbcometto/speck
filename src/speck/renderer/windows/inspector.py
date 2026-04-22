"""Inspector window for an entity"""
import pyglet

from ..windows import SpeckWindow
from ...core import World
from ...utils import _hex_to_rgb
from ...config import SELECTED_COLOR, OTHER_COLOR, GRAY_COLOR, DARK_GRAY_COLOR

class InspectorWindow(SpeckWindow):
    """An inspector window for an entity"""
    def __init__(self, world: World, windows: list, eid: int, width: int = 300, height: int = 400) -> None:
        super().__init__(world, windows, width, height)
        self.eid = eid
        self.window.set_caption(f"Speck Inspector: Entity {eid}")

        pyglet.gl.glClearColor(*_hex_to_rgb(DARK_GRAY_COLOR, return_as_floats=True))
        self.window.push_handlers(self)

        self._batch = pyglet.graphics.Batch()
        self._labels = []

    def on_draw(self) -> None:
        self.window.clear()
        self._build_labels()
        self._batch.draw()

    def on_resize(self, width, height) -> None:
        self.width = width
        self.height = height

    def _build_labels(self) -> None:
        self._labels.clear()
        self._batch = pyglet.graphics.Batch()

        y = self.height - 20

        # Header
        self._labels.append(pyglet.text.Label(
            text=f"Entity {self.eid}",
            x=10, y=y,
            font_name="Consolas",
            font_size=13,
            color=_hex_to_rgb(SELECTED_COLOR),
            batch=self._batch
        ))
        y -= 28

        # Components
        for comp_type, store in self.world.components.items():
            if self.eid in store:
                comp = store[self.eid]

                # Component name
                self._labels.append(pyglet.text.Label(
                    text=comp_type.__name__,
                    x=10, y=y,
                    font_name="Consolas",
                    font_size=11,
                    color=_hex_to_rgb(OTHER_COLOR),
                    batch=self._batch
                ))
                y -= 18

                # Fields
                for field, value in comp.__dict__.items():
                    unit = getattr(comp.__class__, 'units', {}).get(field, "")
                    text = f"  {field}: {value:.4f} {unit}" if isinstance(value, float) else f"  {field}: {value}"
                    self._labels.append(pyglet.text.Label(
                        text=text,
                        x=10, y=y,
                        font_name="Consolas",
                        font_size=10,
                        color=_hex_to_rgb(GRAY_COLOR),
                        batch=self._batch
                    ))
                    y -= 16

                y -= 4  # extra gap between components
        