"""A collection of widgets"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .viewport.camera import Camera

from abc import ABC, abstractmethod
import pyglet
from typing import Callable
from enum import Enum

from ...core import World
from ...components.dynamics import Position
from ...components.assemblies import Assembly
from ...components.rendering import RenderData
from ...utils import _hex_to_rgb
from ...config import SELECTED_COLOR, GRAY_COLOR, OTHER_COLOR, DARK_GRAY_COLOR, ZOOM_FACTOR, MINIMAP_FOCUS_COLOR






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

        if self.anchor_top and not self.anchor_bottom:
            self.y += dh
        if self.anchor_right and not self.anchor_left:
            self.x += dw
        if self.anchor_left and self.anchor_right:
            self.width += dw   # stretch, don't move x
        if self.anchor_top and self.anchor_bottom:
            self.height += dh  # stretch, don't move y

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
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> bool:
        for child in self.children:
            if child.on_mouse_drag(x, y, dx, dy, buttons, modifiers):
                return True
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
    def __init__(self, world: World, input_handler, left_offset = 0, parent_width: int = 800, parent_height: int = 600) -> None:
        super().__init__(x=0, y=0, width=200, height=100,
                         layout="vertical", gap=2, padding=6)
        self.world = world
        self.input_handler = input_handler
        self.left_offset = left_offset
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
        self.x = self.left_offset + 10  # left side
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
                 on_minimap_follow: Callable, left_offset = 0,
                 parent_width: int = 800, parent_height: int = 600) -> None:
        super().__init__(x=0, y=0, width=0, height=40,
                         layout="horizontal", gap=4, padding=4, alpha=0)
        self.world = world
        self.input_handler = input_handler
        self.on_minimap_follow = on_minimap_follow
        self.left_offset = left_offset

        self._built_for_eid: int | None = None
        self._parent_width = parent_width
        self._parent_height = parent_height

    def _default_actions(self, eid: int) -> list[tuple[str, Callable]]:
        actions = [
            ("[f] Follow", lambda: self.input_handler.set_follower(eid)),
            ("[i] Inspect", lambda: self.input_handler.open_inspector(eid)),
            ("[m] Minimap", lambda: self.on_minimap_follow(eid)),
        ]

        if eid in self.world.get_component(Assembly):
            actions.append(("[g] Graph", lambda: self.input_handler.open_graph(eid)))

        return actions

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
        self.x = self.left_offset + 210  # right of selection panel
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
                 anchor_bottom: bool = False, anchor_left: bool = False,
                 padding = 10, border = 3,
                 alpha = 1):
        from .viewport.camera import Camera

        super().__init__(x, y, width, height, anchor_top, anchor_right, anchor_bottom, anchor_left)
        self.world = world
        self.main_camera = main_camera
        self._background: pyglet.shapes.Rectangle | None = None
        self._border: pyglet.shapes.Rectangle | None = None
        self._shapes: list = []
        self._padding = padding
        self.border = border
        self._pressed = False
        self._is_dragging = False
        self.alpha = alpha

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

        # Draw background and border
        if self._background is None:
            self._background = pyglet.shapes.Rectangle(
                x=self.x, y=self.y,
                width=self.width, height=self.height,
                color=_hex_to_rgb(DARK_GRAY_COLOR, self.alpha),
                batch=batch
            )
        else:
            self._background.batch = batch

        if self._border is None:
            self._border = pyglet.shapes.Box(
            x=self.x, y=self.y,
            width=self.width, height=self.height,
            thickness=self.border,
            color=_hex_to_rgb(GRAY_COLOR,self.alpha),
            batch=batch
        )
        else:
            self._border.batch = batch

        



        # Draw entities
        positions = self.world.get_component(Position)

        if not positions:
            return

        self._shapes = []
        for eid, pos in positions.items():
            mx, my = self._world_to_minimap(pos.x, pos.y)
            # cull outside minimap bounds
            if mx < self.x + self.border or mx > self.x + self.width - self.border or my < self.y + self.border or my > self.y + self.height - self.border:
                continue
            color = MINIMAP_FOCUS_COLOR if eid == self._follow_eid else OTHER_COLOR
            tuple_color = _hex_to_rgb(color,self.alpha)
            self._shapes.append(pyglet.shapes.Circle(
                x=mx, y=my, radius=2,
                color=tuple_color,
                batch=batch
            ))



        # Draw main camera viewport indicator
        half_w = self.main_camera.width / 2 / self.main_camera.zoom
        half_h = self.main_camera.height / 2 / self.main_camera.zoom

        # corners of main viewport in world space
        center_x = self.main_camera.x + self.main_camera.origin_x
        center_y = self.main_camera.y + self.main_camera.origin_y

        left   = center_x - half_w
        right  = center_x + half_w
        bottom = center_y - half_h
        top    = center_y + half_h

        # convert to minimap space
        mx1, my1 = self._world_to_minimap(left, bottom)
        mx2, my2 = self._world_to_minimap(right, top)

        # clamp to minimap bounds
        mx1 = max(mx1, self.x + self.border)
        my1 = max(my1, self.y + self.border)
        mx2 = min(mx2, self.x + self.width - self.border)
        my2 = min(my2, self.y + self.height - self.border)

        box_w = mx2 - mx1
        box_h = my2 - my1

        if box_w > 0 and box_h > 0:
            self._shapes.append(pyglet.shapes.Box(
                x=mx1, y=my1,
                width=box_w,
                height=box_h,
                thickness=1,
                color=_hex_to_rgb(SELECTED_COLOR, self.alpha),
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
        if self._border:
            self._border.x = self.x
            self._border.y = self.y
            self._border.width = self.width
            self._border.height = self.height

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
        if buttons & pyglet.window.mouse.LEFT and self._pressed:
            self._is_dragging = True
            self.main_camera.x += dx / self.camera.zoom
            self.main_camera.y += dy / self.camera.zoom
            return True
        return False













class IconStripWidget(PanelWidget):
    """A vertical strip of icon buttons that toggle panels"""
    def __init__(self, world: World, x: int, y: int, width: int, height: int,
                 anchor_top: bool = False, anchor_right: bool = False,
                 anchor_bottom: bool = False, anchor_left: bool = False,
                 bottom_offset = 0) -> None:
        super().__init__(x, y, width, height,
                         color=DARK_GRAY_COLOR,
                         layout="vertical", gap=2, padding=2,
                         anchor_top=anchor_top, anchor_right=anchor_right,
                         anchor_bottom=anchor_bottom, anchor_left=anchor_left)
        self.world = world
        self._panels: dict[str, PanelWidget] = {}
        self._panel_visible: dict[str, bool] = {}
        self.bottom_offset = bottom_offset

    def add_panel(self, key: str, label: str, panel: PanelWidget) -> None:
        """Register a panel and add its toggle button"""
        self._panels[key] = panel
        self._panel_visible[key] = False

        self.add(TextButtonWidget(
            x=0, y=0,
            width=self.width - self.padding * 2,
            height=self.width - self.padding * 2,  # square buttons
            text=label,
            action=lambda k=key: self._toggle(k),
            active=lambda k=key: self._panel_visible[k]
        ))

    def _toggle(self, key: str) -> None:
        self._panel_visible[key] = not self._panel_visible[key]
        self._panels[key].visible = self._panel_visible[key]

    def hit_test(self, x: int, y: int) -> bool:
        if super().hit_test(x, y):
            return True
        for key, panel in self._panels.items():
            if self._panel_visible[key] and panel.hit_test(x, y):
                return True
        return False

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        super().draw(batch)
        for key, panel in self._panels.items():
            if self._panel_visible[key]:
                panel.draw(batch)

    def on_mouse_press(self, x, y, button, modifiers) -> bool:
        for key, panel in self._panels.items():
            if self._panel_visible[key] and panel.hit_test(x, y):
                return panel.on_mouse_press(x, y, button, modifiers)
        return super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers) -> bool:
        for key, panel in self._panels.items():
            if self._panel_visible[key]:
                panel.on_mouse_release(x, y, button, modifiers)
        return super().on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy) -> bool:
        for key, panel in self._panels.items():
            if self._panel_visible[key]:
                panel.on_mouse_motion(x, y, dx, dy)
        return super().on_mouse_motion(x, y, dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y) -> bool:
        for key, panel in self._panels.items():
            if self._panel_visible[key] and panel.hit_test(x, y):
                return panel.on_mouse_scroll(x, y, scroll_x, scroll_y)
        return False

    def on_resize(self, width, height) -> None:
        super().on_resize(width, height)
        for panel in self._panels.values():
            panel.x = self.x + self.width
            panel.y = self.y + self.bottom_offset
            panel.height = self.height - self.bottom_offset
            try:
                panel.bottom_offset = self.bottom_offset
            except:
                pass
            panel._on_reposition()








class EntityListPanelWidget(PanelWidget):
    """A scrollable list of all entities"""
    def __init__(self, world: World, input_handler, x: int, y: int, 
                 width: int, height: int, 
                 bottom_offset = 0, content_padding = 4) -> None:
        super().__init__(x, y, width, height,
                         color=GRAY_COLOR,
                         layout="absolute", gap=0, padding=0)
        self.world = world
        self.input_handler = input_handler
        self._scroll_offset = 0
        self._row_height = 22
        self._labels: list = []
        self._buttons: list = []
        self._header: pyglet.text.Label | None = None
        self.bottom_offset = bottom_offset
        self.content_padding = 4

    def _get_entities(self) -> list[int]:
        positions = self.world.get_component(Position)
        return list(positions.keys())

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        super().draw(batch)

        # Header
        self._header = pyglet.text.Label(
            text="Entities",
            x=self.x + 6, y=self.y + self.height - 20,
            font_name="Consolas",
            font_size=11,
            color=_hex_to_rgb(SELECTED_COLOR),
            batch=batch
        )

        # Entity rows
        entities = self._get_entities()
        total = len(entities)

        content_y = self.y + self.content_padding
        content_height = self.height - 30 - self.content_padding*2

        visible_rows = max(0, content_height // self._row_height)
        max_offset = max(0, total - visible_rows)
        self._scroll_offset = min(self._scroll_offset, max_offset)

        visible = entities[self._scroll_offset:self._scroll_offset + visible_rows]

        self._labels = []
        self._buttons = []
        for i, eid in enumerate(visible):
            y = content_y + content_height - (i + 1) * self._row_height
            color = SELECTED_COLOR if eid == self.input_handler.selected_eid else OTHER_COLOR
            self._labels.append(pyglet.text.Label(
                text=f"[{eid}]",
                x=self.x + 6, y=y + (self._row_height - 11) // 2,
                font_name="Consolas",
                font_size=11,
                color=_hex_to_rgb(color),
                batch=batch
            ))

        # Scrollbar
        if total > visible_rows and content_height > 0 and visible_rows > 0:
            scrollbar_height = content_height
            scrollbar_x = self.x + self.width - 6
            thumb_ratio = visible_rows / total
            thumb_height = max(10, int(scrollbar_height * thumb_ratio))
            
            scroll_ratio = self._scroll_offset / max(1, total - visible_rows)
            thumb_y = content_y + int((scrollbar_height - thumb_height) * (1 - scroll_ratio))


            # track
            self._labels.append(pyglet.shapes.Rectangle(
                x=scrollbar_x, y=content_y,
                width=4, height=scrollbar_height,
                color=_hex_to_rgb(DARK_GRAY_COLOR),
                batch=batch
            ))

            # thumb
            self._labels.append(pyglet.shapes.Rectangle(
                x=scrollbar_x, y=thumb_y,
                width=4, height=thumb_height,
                color=_hex_to_rgb(SELECTED_COLOR),
                batch=batch
            ))

    def on_mouse_press(self, x, y, button, modifiers) -> bool:
        if not self.hit_test(x, y):
            return False
        entities = self._get_entities()
        
        content_y = self.y + self.content_padding
        content_height = self.height - 30 - self.content_padding * 2
        visible_rows = content_height // self._row_height
        
        visible = entities[self._scroll_offset:self._scroll_offset + visible_rows]
        for i, eid in enumerate(visible):
            row_y = content_y + content_height - (i + 1) * self._row_height
            if row_y <= y <= row_y + self._row_height:
                self.input_handler.selected_eid = eid
                return True
        return True

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y) -> bool:
        if self.hit_test(x, y):
            content_height = self.height - 30 - self.content_padding * 2
            visible_rows = content_height // self._row_height
            entities = self._get_entities()
            max_offset = max(0, len(entities) - visible_rows)
            self._scroll_offset = max(0, min(max_offset, self._scroll_offset - int(scroll_y)))
            return True
        return False






class ComponentInspectorWidget(Widget):
    def __init__(self, x, y, width, height, world, eid,
                 anchor_top=False, anchor_right=False,
                 anchor_bottom=False, anchor_left=False,
                 max_col_width = 150, min_col_width = 10,
                 order: list[type] | None = None):
        super().__init__(x, y, width, height, anchor_top, anchor_right, anchor_bottom, anchor_left)
        self.world = world
        self.eid = eid
        self._scroll_offset = 0
        self._row_height = 18
        self._char_width = 7
        self._padding = 4
        self._scrollbar_width = 8
        self._labels = []
        self.max_col_width = max_col_width
        self.min_col_width = min_col_width
        self.order = order

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y) -> bool:
        if self.hit_test(x, y):
            self._scroll_offset = max(0, self._scroll_offset - int(scroll_y))
            return True
        return False

    def _format_field(self, comp, field, value) -> str:
        unit = getattr(comp.__class__, 'units', {}).get(field, "")
        if isinstance(value, float):
            return f"{field}: {value:.3f}{unit}"
        return f"{field}: {value}"

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        max_chars = max(1, max_width // self._char_width)
        if len(text) <= max_chars:
            return [text]
        lines = []
        while text:
            lines.append(text[:max_chars])
            text = "  " + text[max_chars:]
            if len(text) <= max_chars:
                lines.append(text)
                break
        return lines

    def _build_blocks(self) -> list:
        blocks = []
        
        # build in specified order first
        if self.order:
            for comp_type in self.order:
                store = self.world.components.get(comp_type, {})
                if self.eid in store:
                    comp = store[self.eid]
                    block = [(comp_type.__name__, OTHER_COLOR)]
                    for field, value in comp.__dict__.items():
                        text = f"  {self._format_field(comp, field, value)}"
                        for line in self._wrap_text(text, self.max_col_width):
                            block.append((line, GRAY_COLOR))
                    blocks.append(block)

        # then any remaining components not in order
        for comp_type, store in self.world.components.items():
            if comp_type in (self.order or []):
                continue
            if self.eid in store:
                comp = store[self.eid]
                block = [(comp_type.__name__, OTHER_COLOR)]
                for field, value in comp.__dict__.items():
                    text = f"  {self._format_field(comp, field, value)}"
                    for line in self._wrap_text(text, self.max_col_width):
                        block.append((line, GRAY_COLOR))
                blocks.append(block)

        return blocks

    def _arrange_blocks(self, blocks, content_width) -> tuple[list, int]:
        if not blocks:
            return [], content_width

        max_field_width = max(
            max(len(line[0]) * self._char_width + self._padding for line in block)
            for block in blocks
        )
        clamped_width = max(self.min_col_width,
                            min(max_field_width, self.max_col_width))
        cols = max(1, content_width // clamped_width)
        col_width = content_width // cols

        # fill columns top to bottom in order
        total_lines = sum(len(block) for block in blocks)
        target_height = (total_lines + cols - 1) // cols

        col_blocks = [[] for _ in range(cols)]
        total_lines = sum(len(block) for block in blocks)
        target_height = (total_lines + cols - 1) // cols

        current_col = 0
        current_height = 0

        for block in blocks:
            if current_height + len(block) > target_height and current_col < cols - 1:
                current_col += 1
                current_height = 0
            col_blocks[current_col].append(block)
            current_height += len(block)

        # flatten columns to lines
        col_lines = []
        for col in col_blocks:
            lines = []
            for block in col:
                for line in block:
                    lines.append(line)
            col_lines.append(lines)

        max_height = max(len(c) for c in col_lines) if col_lines else 0
        rows = []
        for row_idx in range(max_height):
            row = []
            for col_idx in range(cols):
                if row_idx < len(col_lines[col_idx]):
                    row.append(col_lines[col_idx][row_idx])
                else:
                    row.append(("", GRAY_COLOR))
            rows.append(row)

        return rows, col_width

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        self._labels = []
        content_width = self.width - self._scrollbar_width - self._padding
        blocks = self._build_blocks()
        rows, col_width = self._arrange_blocks(blocks, content_width)

        total_rows = len(rows)
        visible_rows = self.height // self._row_height
        max_offset = max(0, total_rows - visible_rows)
        self._scroll_offset = min(self._scroll_offset, max_offset)

        y = self.y + self.height
        for i in range(self._scroll_offset, min(self._scroll_offset + visible_rows, total_rows)):
            y -= self._row_height
            for j, (text, color) in enumerate(rows[i]):
                if text:
                    self._labels.append(pyglet.text.Label(
                        text=text,
                        x=self.x + self._padding + j * col_width, y=y,
                        font_name="Consolas", font_size=10,
                        color=_hex_to_rgb(color),
                        batch=batch
                    ))

        if total_rows > visible_rows:
            scrollbar_x = self.x + self.width - self._scrollbar_width
            track_height = self.height
            thumb_height = max(20, track_height * visible_rows // total_rows)
            thumb_y = self.y + track_height - int(
                (track_height - thumb_height) * self._scroll_offset / max(1, max_offset)
            ) - thumb_height

            self._labels.append(pyglet.shapes.Rectangle(
                x=scrollbar_x, y=self.y,
                width=self._scrollbar_width, height=track_height,
                color=_hex_to_rgb(DARK_GRAY_COLOR),
                batch=batch
            ))
            self._labels.append(pyglet.shapes.Rectangle(
                x=scrollbar_x, y=thumb_y,
                width=self._scrollbar_width, height=thumb_height,
                color=_hex_to_rgb(GRAY_COLOR),
                batch=batch
            ))

    def _on_reposition(self) -> None:
        self._labels = []










class _FlowNode(Widget):
    HDR_H = 22
    ROW_H = 20
    PR    = 5

    def __init__(self, part_eid, label, ports, wx=0.0, wy=0.0, on_inspect=None):
        # x, y, width, height are in canvas world space
        w = 140
        h = _FlowNode.HDR_H + max(len(ports), 1) * _FlowNode.ROW_H
        super().__init__(wx, wy, w, h)
        self.part_eid = part_eid
        self.label    = label
        self.ports    = ports   # list[tuple[str, PORT_TYPE]]

        self.flipped = False

        btn_h = self.HDR_H - 4
        self._btn_flip = TextButtonWidget(
            0, 0, btn_h, btn_h, text="<>",
            action=lambda: setattr(self, 'flipped', not self.flipped),
            font_size=8, xpadding=2
        )
        self._btn_inspect = TextButtonWidget(
            0, 0, btn_h, btn_h, text="i",
            action=(lambda: on_inspect(part_eid)) if on_inspect else None,
            font_size=8, xpadding=4
        )

    @property
    def buttons(self):
        return [self._btn_flip, self._btn_inspect]

    def hit_test(self, wx, wy):
        return self.x <= wx <= self.x + self.width and self.y <= wy <= self.y + self.height

    def port_world_pos(self, port):
        i      = self.ports.index(port)
        body_h = max(len(self.ports), 1) * self.ROW_H
        ly     = body_h - (i + 0.5) * self.ROW_H
        lx     = 0.0 if self.flipped else float(self.width)
        return self.x + lx, self.y + ly

    def port_at(self, wx, wy, zoom):
        r = self.PR * 2 / zoom
        for port in self.ports:
            px, py = self.port_world_pos(port)
            if (wx - px)**2 + (wy - py)**2 <= r**2:
                return port
        return None

    def draw(self, batch, to_screen, zoom, selected, shapes):
        sx, sy = to_screen(self.x, self.y)
        sw     = self.width  * zoom
        sh     = self.height * zoom
        hh     = self.HDR_H  * zoom
        fsz    = max(11, int(9 * zoom))
        border = _hex_to_rgb(SELECTED_COLOR if selected else OTHER_COLOR)

        shapes += [
            pyglet.shapes.Rectangle(sx, sy, sw, sh, color=_hex_to_rgb(DARK_GRAY_COLOR), batch=batch),
            pyglet.shapes.Box(sx, sy, sw, sh, thickness=1, color=border, batch=batch),
            pyglet.shapes.Rectangle(sx, sy + sh - hh, sw, hh, color=_hex_to_rgb(GRAY_COLOR), batch=batch),
            pyglet.text.Label(self.label, x=sx + 4*zoom, y=sy + sh - hh + 4*zoom,
                              font_name="Consolas", font_size=fsz,
                              color=_hex_to_rgb(SELECTED_COLOR), batch=batch),
        ]

        # update and draw header buttons in screen space
        btn_h = max(8, int(hh - 4))
        for i, btn in enumerate(self.buttons):
            btn.width  = btn_h
            btn.height = btn_h
            btn.x = int(sx + sw - (i + 1) * (btn_h + 2))
            btn.y = int(sy + sh - hh + 2)
            btn._on_reposition()
            btn.draw(batch)

        for port in self.ports:
            px, py = to_screen(*self.port_world_pos(port))
            pr = self.PR * zoom
            shapes += [
                pyglet.shapes.Circle(px, py, pr, color=_hex_to_rgb(OTHER_COLOR), batch=batch),
                pyglet.text.Label(
                    port[0],
                    x=px + (pr + 2 if self.flipped else -pr - 2),
                    y=py - fsz // 2,
                    font_name="Consolas", font_size=max(6, fsz - 1),
                    color=_hex_to_rgb(OTHER_COLOR),
                    anchor_x="left" if self.flipped else "right",
                    batch=batch
                ),
            ]

    def _on_reposition(self):
        pass






class FlowgraphCanvasWidget(Widget):

    BEZIER_SEGS = 20
    CTRL        = 70

    def __init__(self, x, y, width, height, on_inspect=None):
        super().__init__(x, y, width, height)
        self._on_inspect = on_inspect
        self._cam_x    = 0.0
        self._cam_y    = 0.0
        self._cam_zoom = 1.0
        self.nodes  = []   # list[_FlowNode]
        self.edges  = []   # list[tuple[_FlowNode, port, _FlowNode, port]]
        self._state      = "idle"   # idle | panning | drag_node | draw_edge
        self._drag_node  = None
        self._edge_src   = None
        self._edge_port  = None
        self._edge_cur   = None
        self._selected   = None
        self._shapes     = []



    # transforms

    def _to_screen(self, wx, wy):
        sx = (wx - self._cam_x) * self._cam_zoom + self.x + self.width  / 2
        sy = (wy - self._cam_y) * self._cam_zoom + self.y + self.height / 2
        return sx, sy

    def _to_world(self, sx, sy):
        wx = (sx - self.x - self.width  / 2) / self._cam_zoom + self._cam_x
        wy = (sy - self.y - self.height / 2) / self._cam_zoom + self._cam_y
        return wx, wy



    # loading

    def load_assembly(self, assembly_eid: int, world: World):
        from ...components.assemblies import Assembly, PartIdentity, FlowgraphLayout
        self.nodes.clear()
        self.edges.clear()
        assemblies = world.get_component(Assembly)
        identities = world.get_component(PartIdentity)

        if assembly_eid not in assemblies:
            return
        
        assembly = assemblies[assembly_eid]
        eid_to_node = {}

        # Build nodes
        for i, part_eid in enumerate(assembly.parts):
            identity = identities.get(part_eid)
            if identity is None:
                continue
            node = _FlowNode(
                part_eid, identity.name or f"Part {part_eid}",
                identity.ports,
                wx=(i % 4) * (_FlowNode.HDR_H + 80),
                wy=-(i // 4) * 180,
                on_inspect=self._on_inspect
            )
            self.nodes.append(node)
            eid_to_node[part_eid] = node

        # Apply saved positions
        layouts = world.get_component(FlowgraphLayout)
        layout = layouts.get(assembly_eid)
        if layout:
            for node in self.nodes:
                if node.part_eid in layout.positions:
                    node.x, node.y = layout.positions[node.part_eid]
                if node.part_eid in layout.flipped:
                    node.flipped = layout.flipped[node.part_eid]

        # Connect nodes
        for from_eid, from_port, to_eid, to_port in assembly.edges:
            a = eid_to_node.get(from_eid)
            b = eid_to_node.get(to_eid)
            if a and b:
                pa = next((p for p in a.ports if p[0] == from_port), None)
                pb = next((p for p in b.ports if p[0] == to_port),   None)
                if pa and pb:
                    self.edges.append((a, pa, b, pb))

    def write_back(self, assembly: Assembly):
        assembly.edges = [(a.part_eid, pa[0], b.part_eid, pb[0])
                          for a, pa, b, pb in self.edges]
        
    def save_layout(self, assembly_eid: int, world: World):
        from ...components.assemblies import FlowgraphLayout
        layouts = world.get_component(FlowgraphLayout)
        if assembly_eid not in layouts:
            world.add_component(assembly_eid, FlowgraphLayout())
            layouts = world.get_component(FlowgraphLayout)

        layouts[assembly_eid].positions = {n.part_eid: (n.x, n.y) for n in self.nodes}
        layouts[assembly_eid].flipped   = {n.part_eid: n.flipped for n in self.nodes}


    def _bezier(self, p0, p1, d0, d1, color, batch):
        x0, y0 = p0
        x1, y1 = p1
        ctrl = self.CTRL * self._cam_zoom
        cx0, cy0 = x0 + d0 * ctrl, y0
        cx1, cy1 = x1 + d1 * ctrl, y1
        def b(t):
            mt = 1 - t
            return (mt**3*x0 + 3*mt**2*t*cx0 + 3*mt*t**2*cx1 + t**3*x1,
                    mt**3*y0 + 3*mt**2*t*cy0 + 3*mt*t**2*cy1 + t**3*y1)
        pts = [b(i / self.BEZIER_SEGS) for i in range(self.BEZIER_SEGS + 1)]
        for a, b_ in zip(pts, pts[1:]):
            self._shapes.append(pyglet.shapes.Line(
                a[0], a[1], b_[0], b_[1], thickness=1, color=color, batch=batch))



    # Draw

    def draw(self, batch):
        self._shapes = []
        self._shapes.append(pyglet.shapes.Rectangle(
            self.x, self.y, self.width, self.height,
            color=_hex_to_rgb(DARK_GRAY_COLOR), batch=batch))

        for a, pa, b, pb in self.edges:
            p0 = self._to_screen(*a.port_world_pos(pa))
            p1 = self._to_screen(*b.port_world_pos(pb))
            d0 = -1 if a.flipped else 1
            d1 = -1 if b.flipped else 1
            self._bezier(p0, p1, d0, d1, _hex_to_rgb(OTHER_COLOR), batch)

        if self._state == "draw_edge" and self._edge_src and self._edge_cur:
            p0 = self._to_screen(*self._edge_src.port_world_pos(self._edge_port))
            p1 = self._to_screen(*self._edge_cur)
            d0 = -1 if self._edge_src.flipped else 1
            self._bezier(p0, p1, d0, 1, _hex_to_rgb(SELECTED_COLOR), batch)

        for node in self.nodes:
            node.draw(batch, self._to_screen, self._cam_zoom,
                      node is self._selected, self._shapes)

    def _edge_at(self, wx, wy, threshold=8.0):
        """Return index of edge under world-space point, or None."""
        t = threshold / self._cam_zoom
        for i, (a, pa, b, pb) in enumerate(self.edges):
            x0, y0 = a.port_world_pos(pa)
            x1, y1 = b.port_world_pos(pb)
            # point-to-segment distance
            dx, dy = x1 - x0, y1 - y0
            if dx == 0 and dy == 0:
                continue
            s = max(0, min(1, ((wx - x0)*dx + (wy - y0)*dy) / (dx*dx + dy*dy)))
            px, py = x0 + s*dx, y0 + s*dy
            if (wx - px)**2 + (wy - py)**2 <= t**2:
                return i
        return None

    # Handlers

    def on_mouse_press(self, x, y, button, modifiers):  
        if not self.hit_test(x, y):
            return False
        

        if button == pyglet.window.mouse.LEFT:
            # buttons are screen-space — check before world conversion
            for node in reversed(self.nodes):
                for btn in node.buttons:
                    if btn.on_mouse_press(x, y, button, modifiers):
                        return True

            wx, wy = self._to_world(x, y)
            for node in reversed(self.nodes):
                port = node.port_at(wx, wy, self._cam_zoom)
                if port:
                    self._state, self._edge_src, self._edge_port, self._edge_cur = \
                        "draw_edge", node, port, (wx, wy)
                    return True
                
            for node in reversed(self.nodes):
                if node.hit_test(wx, wy):
                    self._state, self._drag_node, self._selected = \
                        "drag_node", node, node
                    return True
            self._state, self._selected = "panning", None
            return True
        
        # Deleting edges
        if button == pyglet.window.mouse.RIGHT:
            i = self._edge_at(wx, wy)
            if i is not None:
                self.edges.pop(i)
                return True
    
        return False

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            for node in self.nodes:
                for btn in node.buttons:
                    btn.on_mouse_release(x, y, button, modifiers)

            if self._state == "draw_edge":
                wx, wy = self._to_world(x, y)
                for node in self.nodes:
                    if node is self._edge_src:
                        continue
                    port = node.port_at(wx, wy, self._cam_zoom)
                    if port and port[1] == self._edge_port[1]:
                        self.edges.append((self._edge_src, self._edge_port, node, port))
                        break
            self._state = "idle"
            self._drag_node = self._edge_src = self._edge_port = self._edge_cur = None
        return False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self._state == "panning":
            self._cam_x -= dx / self._cam_zoom
            self._cam_y -= dy / self._cam_zoom
            return True
        if self._state == "drag_node" and self._drag_node:
            self._drag_node.x += dx / self._cam_zoom
            self._drag_node.y += dy / self._cam_zoom
            return True
        if self._state == "draw_edge":
            self._edge_cur = self._to_world(x, y)
            return True
        return False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.hit_test(x, y):
            return False
        wx0, wy0 = self._to_world(x, y)
        self._cam_zoom *= ZOOM_FACTOR if scroll_y > 0 else 1 / ZOOM_FACTOR
        wx1, wy1 = self._to_world(x, y)
        self._cam_x -= wx1 - wx0
        self._cam_y -= wy1 - wy0
        return True
    
    def on_mouse_motion(self, x, y, dx, dy):
        for node in self.nodes:
            for btn in node.buttons:
                btn.on_mouse_motion(x, y, dx, dy)
        return False

    def _on_reposition(self):
        pass







