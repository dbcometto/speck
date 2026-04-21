"""An inspector window for an entity"""
import pyglet
import time

from ...core.world import World
from .window import SpeckWindow

class InspectorWindow(SpeckWindow):
     """A window opening an entity inspector"""
     def __init__(self, world: World, windows: list[SpeckWindow], width: int = 800, height: int = 600):
        """Establish the Pyglet renderer"""
        super().__init__(world, windows, width, height) # creates window, hud, camera, and input handler
        self._last_draw = time.perf_counter()
        self.windows.append(self.window)     

        # Pyglet State
        pyglet.gl.glClearColor(0.05, 0.05, 0.05, 1.0)
        self.window.push_handlers(self)
        self.window.push_handlers(self.hud)
        self.window.push_handlers(self.camera)
        self.window.push_handlers(self.input_handler)

        self._batch = pyglet.graphics.Batch()
        self._labels = []
        self._build_labels()

    def _build_labels(self) -> None:
        self._labels.clear()
        self._batch = pyglet.graphics.Batch()

        y = self.window.height - 20
        # Entity header
        self._labels.append(pyglet.text.Label(
            text=f"Entity {self.eid}",
            x=10, y=y,
            font_name="Consolas",
            font_size=12,
            bold=True,
            color=(255, 255, 255, 255),
            batch=self._batch
        ))
        y -= 25

        # Component list
        for comp_type, store in self.world.components.items():
            if self.eid in store:
                comp = store[self.eid]
                self._labels.append(pyglet.text.Label(
                    text=f"{comp_type.__name__}",
                    x=10, y=y,
                    font_name="Consolas",
                    font_size=11,
                    color=(200, 200, 200, 255),
                    batch=self._batch
                ))
                y -= 18
                # Component fields
                for field, value in comp.__dict__.items():
                    self._labels.append(pyglet.text.Label(
                        text=f"  {field}: {value:.3f}" if isinstance(value, float) else f"  {field}: {value}",
                        x=10, y=y,
                        font_name="Consolas",
                        font_size=10,
                        color=(150, 150, 150, 255),
                        batch=self._batch
                    ))
                    y -= 16

    def on_draw(self) -> None:
        self.window.clear()
        self._build_labels()
        self._batch.draw()

    def on_resize(self, width, height) -> None:
        self._build_labels()