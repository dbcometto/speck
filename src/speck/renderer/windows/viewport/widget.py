"""A collection of widgets"""
from abc import ABC, abstractmethod
import pyglet
from typing import Callable
from enum import Enum

from ....core import World
from ....components.dynamics import Position
from ....components.rendering import RenderData
from .camera import Camera
from ....utils import _hex_to_rgb
from ....config import SELECTED_COLOR, GRAY_COLOR, OTHER_COLOR, DARK_GRAY_COLOR, ZOOM_FACTOR, MINIMAP_FOCUS_COLOR






class Widget(ABC):
    """Base widget class"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 anchor_top: bool = False,
                 anchor_right: bool = False,
                 anchor_bottom: bool = False,
                 anchor_left: bool = False) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.anchor_top = anchor_top
        self.anchor_right = anchor_right
        self.anchor_bottom = anchor_bottom
        self.anchor_left = anchor_left
        self._prev_parent_width = 0
        self._prev_parent_height = 0

    def hit_test(self, x: int, y: int) -> bool:
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    @abstractmethod
    def draw(self, batch: pyglet.graphics.Batch) -> None: ...

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool:
        return False
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> bool:
        return False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool:
        return False
    
    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> bool:
        return False
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> bool:
        return False

    def on_resize(self, width: int, height: int) -> None:
        if self._prev_parent_width == 0:
            self._prev_parent_width = width
            self._prev_parent_height = height
            return
    
        dw = width - self._prev_parent_width
        dh = height - self._prev_parent_height

        if self.anchor_top:
            self.y += dh
        if self.anchor_right:
            self.x += dw
        if self.anchor_right and not self.anchor_left:
            pass  # x already moved
        if self.anchor_left and self.anchor_right:
            self.width += dw  # stretch horizontally
        if self.anchor_top and self.anchor_bottom:
            self.height += dh  # stretch vertically

        self._prev_parent_width = width
        self._prev_parent_height = height

        self._on_reposition()

    def _on_reposition(self) -> None:
        """Called after position/size changes — subclasses update their pyglet objects"""
        pass




class ClickableWidget(Widget):
    """Mixin that adds click/hover behavior"""
    def __init__(self, x, y, width, height, action=None, active=None):
        super().__init__(x, y, width, height)
        self.action = action
        self.active = active
        self._hovered = False
        self._pressed = False

    def on_mouse_press(self, x, y, button, modifiers) -> bool:
        if self.hit_test(x, y):
            self._pressed = True
            return True
        return False

    def on_mouse_release(self, x, y, button, modifiers) -> bool:
        if self._pressed and self.hit_test(x, y):
            if self.action:
                self.action()
            self._pressed = False
            return True
        self._pressed = False
        return False

    def on_mouse_motion(self, x, y, dx, dy) -> bool:
        self._hovered = self.hit_test(x, y)
        return False






class TextWidget(Widget):
    def __init__(self, x, y, width, height,
                 text: str | Callable[[], str] = "",
                 font_name="Consolas", font_size=11,
                 color=OTHER_COLOR, background_color=GRAY_COLOR, background_alpha=1,
                 anchor_top=False, anchor_right=False, anchor_bottom=False, anchor_left=False,
                 xpadding = 4):
        super().__init__(x, y, width, height, anchor_top, anchor_right, anchor_bottom, anchor_left)
        self._text = text
        self.font_name = font_name
        self.font_size = font_size
        self.xpadding = xpadding
        self.color = color
        self.background_color = background_color
        self.background_alpha = background_alpha
        self._label: pyglet.text.Label | None = None
        self._background: pyglet.shapes.Rectangle | None = None

    @property
    def text(self) -> str:
        return self._text() if callable(self._text) else self._text

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        if self._background is None:
            self._background = pyglet.shapes.Rectangle(
                x=self.x, y=self.y,
                width=self.width, height=self.height,
                color=_hex_to_rgb(self.background_color, self.background_alpha),
                batch=batch
            )
        else:
            self._background.color = _hex_to_rgb(self.background_color, self.background_alpha)
            self._background.batch = batch

        if self._label is None:
            label_y = self.y + (self.height - self.font_size) // 2
            self._label = pyglet.text.Label(
                text=self.text,
                x=self.x+self.xpadding, y=label_y,
                font_name=self.font_name,
                font_size=self.font_size,
                color=_hex_to_rgb(self.color),
                batch=batch
            )
        else:
            self._label.text = self.text
            self._label.color = _hex_to_rgb(self.color)
            self._label.batch = batch

    def _on_reposition(self) -> None:
        if self._label:
            self._label.x = self.x + self.xpadding
            self._label.y = self.y + (self.height - self.font_size) // 2
        if self._background:
            self._background.x = self.x
            self._background.y = self.y
            self._background.width = self.width
            self._background.height = self.height






class TextButtonWidget(ClickableWidget, TextWidget):
    """A clickable text button"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str = "",
                 action: Callable | None = None,
                 active: Callable[[], bool] | None = None,
                 font_name: str = "Consolas",
                 font_size: int = 11,
                 color: str = OTHER_COLOR,
                 background_color: str = GRAY_COLOR,
                 active_color: str = SELECTED_COLOR,
                 hover_color: str = SELECTED_COLOR,
                 background_alpha: int = 1,
                 xpadding: int = 4,
                 anchor_top: bool = False,
                 anchor_right: bool = False,
                 anchor_bottom: bool = False,
                 anchor_left: bool = False) -> None:
        TextWidget.__init__(self, x, y, width, height,
                            text=text,
                            font_name=font_name,
                            font_size=font_size,
                            color=color,
                            background_color=background_color,
                            background_alpha=background_alpha,
                            anchor_top=anchor_top,
                            anchor_right=anchor_right,
                            anchor_bottom=anchor_bottom,
                            anchor_left=anchor_left,
                            xpadding=xpadding)
        self.action = action
        self.active = active

        self._hovered = False
        self._pressed = False

        self.active_color = active_color
        self.hover_color = hover_color

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        # Override color based on state before drawing
        if self.active and self.active():
            self.color = self.active_color
        elif self._hovered:
            self.color = self.hover_color
        else:
            self.color = OTHER_COLOR
        TextWidget.draw(self, batch)






class Layout(Enum):
    ABSOLUTE = "absolute"
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    GRID = "grid"

class PanelWidget(Widget):
    """A container widget with a background and layout"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 color: str = GRAY_COLOR,
                 alpha: float = 1,
                 layout: str = "absolute",
                 gap: int = 4,
                 padding: int = 4,
                 columns: int = 2,
                 anchor_top: bool = False,
                 anchor_right: bool = False,
                 anchor_bottom: bool = False,
                 anchor_left: bool = False) -> None:
        super().__init__(x, y, width, height, anchor_top, anchor_right, anchor_bottom, anchor_left)
        self.color = color
        self.alpha = alpha
        self.layout = Layout(layout)
        self.gap = gap
        self.padding = padding
        self.columns = columns
        self.children: list[Widget] = []
        self._background: pyglet.shapes.Rectangle | None = None

    def add(self, widget: Widget) -> None:
        self.children.append(widget)
        self._apply_layout()

    def _apply_layout(self) -> None:
        if self.layout == Layout.ABSOLUTE:
            return

        elif self.layout == Layout.VERTICAL:
            # stack top to bottom
            cursor_y = self.y + self.height - self.padding
            for child in self.children:
                cursor_y -= child.height
                child.x = self.x + self.padding
                child.y = cursor_y
                child._on_reposition()
                cursor_y -= self.gap

        elif self.layout == Layout.HORIZONTAL:
            # stack left to right
            cursor_x = self.x + self.padding
            for child in self.children:
                child.x = cursor_x
                child.y = self.y + self.padding
                child._on_reposition()
                cursor_x += child.width + self.gap

        elif self.layout == Layout.GRID:
            cell_width = (self.width - self.padding * 2 - self.gap * (self.columns - 1)) // self.columns
            for i, child in enumerate(self.children):
                col = i % self.columns
                row = i // self.columns
                child.width = cell_width
                child.x = self.x + self.padding + col * (cell_width + self.gap)
                child.y = self.y + self.height - self.padding - (row + 1) * (child.height + self.gap) + self.gap
                child._on_reposition()

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        if self._background is None:
            self._background = pyglet.shapes.Rectangle(
                x=self.x, y=self.y,
                width=self.width, height=self.height,
                color=_hex_to_rgb(self.color, self.alpha),
                batch=batch
            )
        else:
            self._background.color = _hex_to_rgb(self.color, self.alpha)
            self._background.batch = batch

        for child in self.children:
            if child.visible:
                child.draw(batch)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool:
        for child in reversed(self.children):
            if child.hit_test(x, y) and child.on_mouse_press(x, y, button, modifiers):
                return True
        return False
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> bool:
        for child in reversed(self.children):
            if child.on_mouse_release(x, y, button, modifiers):
                return True
        return False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool:
        for child in self.children:
            child.on_mouse_motion(x, y, dx, dy)
        return False

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self._on_reposition()
        self._apply_layout()
        for child in self.children:
            child.on_resize(width, height)

    def _on_reposition(self) -> None:
        if self._background:
            self._background.x = self.x
            self._background.y = self.y
            self._background.width = self.width
            self._background.height = self.height









class SelectionPanelWidget(PanelWidget):
    """Shows info about the selected entity"""
    def __init__(self, world: World, input_handler, parent_width: int = 800, parent_height: int = 600) -> None:
        super().__init__(x=0, y=0, width=200, height=100,
                         layout="vertical", gap=2, padding=6)
        self.world = world
        self.input_handler = input_handler
        self._built_for_eid: int | None = None
        self._parent_width = parent_width
        self._parent_height = parent_height
        self._reposition_to_corner()



    def _build(self, eid: int) -> None:
        self.children.clear()
        self._built_for_eid = eid

        self.add(TextWidget(
            x=0, y=0, width=self.width - self.padding * 2, height=30,
            text=f"Entity {eid}",
            font_size=12
        ))

        total_height = self.padding * 2
        for child in self.children:
            total_height += child.height + self.gap
        self.height = min(total_height, self._parent_height - 20)
        self._on_reposition()
        self._apply_layout()
        self._reposition_to_corner()

    def _reposition_to_corner(self) -> None:
        self.x = 10  # left side
        self.y = 10
        self._on_reposition()

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        eid = self.input_handler.selected_eid
        if eid is None:
            return
        if eid != self._built_for_eid:
            self._build(eid)
        super().draw(batch)

    def on_mouse_press(self, x, y, button, modifiers) -> bool:
        if self.input_handler.selected_eid is None:
            return False
        return super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers) -> bool:
        if self.input_handler.selected_eid is None:
            return False
        return super().on_mouse_release(x, y, button, modifiers)

    def on_resize(self, width, height) -> None:
        self._parent_width = width
        self._parent_height = height
        if self._built_for_eid is not None:
            self._build(self._built_for_eid)
        self._reposition_to_corner()





class ActionBarWidget(PanelWidget):
    """Shows actions for the selected entity"""
    def __init__(self, world: World, input_handler, 
                 on_minimap_follow: Callable,
                 parent_width: int = 800, parent_height: int = 600) -> None:
        super().__init__(x=0, y=0, width=0, height=40,
                         layout="horizontal", gap=4, padding=4, alpha=0)
        self.world = world
        self.input_handler = input_handler
        self.on_minimap_follow = on_minimap_follow
        self._built_for_eid: int | None = None
        self._parent_width = parent_width
        self._parent_height = parent_height

    def _default_actions(self, eid: int) -> list[tuple[str, Callable]]:
        return [
            ("[f] Follow", lambda: self.input_handler.set_follower(eid)),
            ("[i] Inspect", lambda: self.input_handler.open_inspector(eid)),
            ("[m] Minimap", lambda: self.on_minimap_follow(eid)),
        ]

    def _build(self, eid: int) -> None:
        self.children.clear()
        self._built_for_eid = eid

        actions = self._default_actions(eid)

        # TODO: add script actions here
        # script = self.world.get_component(ScriptComponent).get(eid)
        # if script:
        #     actions += script.actions

        for text, action in actions:
            self.add(TextButtonWidget(
                x=0, y=0, width=90, height=30,
                text=text,
                font_size=10,
                action=action
            ))

        # auto-resize width
        total_width = self.padding * 2
        for child in self.children:
            total_width += child.width + self.gap
        self.width = total_width
        self._on_reposition()
        self._apply_layout()
        self._reposition()

    def _reposition(self) -> None:
        self.x = 210  # right of selection panel
        self.y = 10
        self._on_reposition()

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        eid = self.input_handler.selected_eid
        if eid is None:
            return
        if eid != self._built_for_eid:
            self._build(eid)
        super().draw(batch)

    def on_mouse_press(self, x, y, button, modifiers) -> bool:
        if self.input_handler.selected_eid is None:
            return False
        return super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers) -> bool:
        if self.input_handler.selected_eid is None:
            return False
        return super().on_mouse_release(x, y, button, modifiers)

    def on_resize(self, width, height) -> None:
        self._parent_width = width
        self._parent_height = height
        if self._built_for_eid is not None:
            self._build(self._built_for_eid)
        self._reposition()








class MinimapWidget(Widget):
    def __init__(self, world: World, x: int, y: int, width: int, height: int,
                 main_camera: Camera,
                 view_range: float = 1000.0,
                 anchor_top: bool = False, anchor_right: bool = False,
                 anchor_bottom: bool = False, anchor_left: bool = False):
        super().__init__(x, y, width, height, anchor_top, anchor_right, anchor_bottom, anchor_left)
        self.world = world
        self.main_camera = main_camera
        self._background: pyglet.shapes.Rectangle | None = None
        self._shapes: list = []
        self._padding = 10
        self._pressed = False
        self._is_dragging = False

        self._follow_eid: int | None = None

        # Minimap camera
        self.camera = Camera(width, height)
        self.camera.zoom = min(
            (width - self._padding * 2) / (view_range * 2),
            (height - self._padding * 2) / (view_range * 2)
        )

    def _world_to_minimap(self, wx, wy) -> tuple[float, float]:
        """Convert world coords to minimap screen coords"""
        sx = (wx - self.camera.x) * self.camera.zoom + self.x + self.width / 2
        sy = (wy - self.camera.y) * self.camera.zoom + self.y + self.height / 2
        return sx, sy

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y) -> bool:
        if self.hit_test(x, y):
            self.camera.zoom *= ZOOM_FACTOR if scroll_y > 0 else 1 / ZOOM_FACTOR
            return True
        return False

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        # Update minimap camera position
        if self._follow_eid is not None:
            positions = self.world.get_component(Position)
            if self._follow_eid in positions:
                pos = positions[self._follow_eid]
                self.camera.x = pos.x
                self.camera.y = pos.y
        else:
            self.camera.x = 0.0
            self.camera.y = 0.0

        if self._background is None:
            self._background = pyglet.shapes.Rectangle(
                x=self.x, y=self.y,
                width=self.width, height=self.height,
                color=_hex_to_rgb(DARK_GRAY_COLOR),
                batch=batch
            )
            self._background.opacity = 128
        else:
            self._background.opacity = 128
            self._background.batch = batch

        positions = self.world.get_component(Position)

        if not positions:
            return

        self._shapes = []
        for eid, pos in positions.items():
            mx, my = self._world_to_minimap(pos.x, pos.y)
            # cull outside minimap bounds
            if mx < self.x or mx > self.x + self.width or my < self.y or my > self.y + self.height:
                continue
            color = MINIMAP_FOCUS_COLOR if eid == self._follow_eid else OTHER_COLOR
            tuple_color = _hex_to_rgb(color)
            self._shapes.append(pyglet.shapes.Circle(
                x=mx, y=my, radius=2,
                color=tuple_color,
                batch=batch
            ))



        # Draw main camera viewport indicator
        half_w = self.main_camera.width / 2 / self.main_camera.zoom
        half_h = self.main_camera.height / 2 / self.main_camera.zoom

        # corners of main viewport in world space
        left   = self.main_camera.x - half_w
        right  = self.main_camera.x + half_w
        bottom = self.main_camera.y - half_h
        top    = self.main_camera.y + half_h

        # convert to minimap space
        mx1, my1 = self._world_to_minimap(left, bottom)
        mx2, my2 = self._world_to_minimap(right, top)

        # clamp to minimap bounds
        mx1 = max(mx1, self.x)
        my1 = max(my1, self.y)
        mx2 = min(mx2, self.x + self.width)
        my2 = min(my2, self.y + self.height)

        box_w = mx2 - mx1
        box_h = my2 - my1

        if box_w > 0 and box_h > 0:
            self._shapes.append(pyglet.shapes.Box(
                x=mx1, y=my1,
                width=box_w,
                height=box_h,
                thickness=1,
                color=_hex_to_rgb(SELECTED_COLOR),
                batch=batch
            ))




    def _on_reposition(self) -> None:
        self.camera.width = self.width
        self.camera.height = self.height
        if self._background:
            self._background.x = self.x
            self._background.y = self.y
            self._background.width = self.width
            self._background.height = self.height

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)

    def on_mouse_press(self, x, y, button, modifiers) -> bool:
        if self.hit_test(x, y) and button == pyglet.window.mouse.LEFT:
            self._pressed = True
            self._is_dragging = False

            wx = (x - self.x - self.width / 2) / self.camera.zoom + self.camera.x
            wy = (y - self.y - self.height / 2) / self.camera.zoom + self.camera.y
            self.main_camera.x = wx
            self.main_camera.y = wy
            
            return True
        self._pressed = False
        return False

    def on_mouse_release(self, x, y, button, modifiers) -> bool:
        if self.hit_test(x, y) and button == pyglet.window.mouse.LEFT:
            if not self._is_dragging and self._pressed:
                self._is_dragging = False
            self._pressed = False
        return False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> bool:
        if self.hit_test(x, y) and buttons & pyglet.window.mouse.LEFT and self._pressed:
            self._is_dragging = True
            self.main_camera.x += dx / self.camera.zoom
            self.main_camera.y += dy / self.camera.zoom
            return True
        return False














