"""Inspector window for an entity"""
import pyglet

from ..windows import SpeckWindow
from ...core import World

class InspectorWindow(SpeckWindow):
    """An inspector window for an entity"""
    def __init__(self, world: World, windows: list, eid: int, width: int = 300, height: int = 400) -> None:
        """Establish the inspector window"""
        super().__init__(world, windows, width, height)
        self.eid = eid
        self.window.set_caption(f"Speck Inspector: Entity {eid}")

        pyglet.gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        self.window.push_handlers(self)

        self._batch = pyglet.graphics.Batch()
        self._labels = []



    # Pyglet Handlers

    def on_draw(self) -> None:
        self.window.clear()
        self._build_labels()
        self._batch.draw()



    # Helpers

    def _build_labels(self) -> None:
        self._labels.clear()
        self._batch = pyglet.graphics.Batch()

        y = self.height - 20

        self._labels.append(pyglet.text.Label(
            text=f"Entity {self.eid}",
            x=10, y=y,
            font_name="Consolas",
            font_size=12,
            color=(255, 255, 255, 255),
            batch=self._batch
        ))
        y -= 25

        for comp_type, store in self.world.components.items():
            if self.eid in store:
                comp = store[self.eid]

                self._labels.append(pyglet.text.Label(
                    text=comp_type.__name__,
                    x=10, y=y,
                    font_name="Consolas",
                    font_size=11,
                    color=(200, 200, 200, 255),
                    batch=self._batch
                ))
                y -= 18

                for field, value in comp.__dict__.items():
                    unit = getattr(comp.__class__, 'units', {}).get(field, "")
                    text = f"  {field}: {value:.4f} {unit}" if isinstance(value, float) else f"  {field}: {value}"
                    self._labels.append(pyglet.text.Label(
                        text=text,
                        x=10, y=y,
                        font_name="Consolas",
                        font_size=10,
                        color=(150, 150, 150, 255),
                        batch=self._batch
                    ))
                    y -= 16