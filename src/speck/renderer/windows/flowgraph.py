"""The assembly flowgraph editor"""
import pyglet

from ..windows import SpeckWindow
from ...core import World
from ...utils import _hex_to_rgb
from ...config import DARK_GRAY_COLOR, SELECTED_COLOR, OTHER_COLOR, GRAY_COLOR
from ...config import KEYBINDS
from .widgets import FlowgraphCanvasWidget, TextWidget
from ...components.assemblies import Assembly
from ...components.functional import Identity

class FlowgraphWindow(SpeckWindow):
    TITLE_PADDING = 35

    def __init__(self, world: World, windows: list, assembly_eid: int,
                 width: int = 700, height: int = 500) -> None:
        super().__init__(world, windows, width, height)
        self.assembly_eid = assembly_eid
        self.window.set_caption(f"Speck Flowgraph: Entity {assembly_eid}")
        pyglet.gl.glClearColor(*_hex_to_rgb(DARK_GRAY_COLOR, return_as_floats=True))
        self.window.push_handlers(self)

        self._assembly = world.get_component(Assembly).get(assembly_eid)
        self._canvas = FlowgraphCanvasWidget(0, 0, width, height, on_inspect=lambda eid: self.open_inspector(eid))
        self._canvas.load_assembly(assembly_eid, world)

        # Title widget
        identity = world.get_component(Identity).get(assembly_eid)
        label = identity.name if identity else f"Entity {assembly_eid}"

        self._title = TextWidget(
            x=8, y=height - self.TITLE_PADDING,
            width=300, height=20,
            text=label,
            font_size=12,
            color=SELECTED_COLOR,
            background_alpha=0,
            anchor_top=True, anchor_left=True
        )



    def open_inspector(self, eid: int| None) -> None:
        """Open an inspector window for an entity"""
        from ...renderer.windows.inspector import InspectorWindow
        # check if already open
        if eid is not None:
            for w in self.windows:
                if isinstance(w, InspectorWindow) and w.eid == eid:
                    w.window.activate()
                    return
            
            new_window = InspectorWindow(self.world, self.windows, eid) # adds itself to the list of windows


    # Pyglet Handlers

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
        if self._assembly is not None:
            self._canvas.write_back(self._assembly)
            self._canvas.save_layout(self.assembly_eid,self.world)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._canvas.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self._canvas.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_motion(self, x, y, dx, dy):
        self._canvas.on_mouse_motion(x, y, dx, dy)

    def on_close(self):
        super().on_close()

    def on_key_press(self, symbol, modifiers) -> None:
        handled = False

        # Entity Interactions
        if symbol in KEYBINDS["inspect"]:
            eid = self._canvas._selected.part_eid
            self.open_inspector(eid)
            handled = True

        return handled