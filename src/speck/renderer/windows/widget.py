"""A collection of widgets"""
from abc import ABC, abstractmethod
import pyglet
from typing import Callable
from enum import Enum

from ...core import World
from ...components.dynamics import Position
from ...components.rendering import RenderData
from .viewport.camera import Camera
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


