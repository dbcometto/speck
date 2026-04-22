"""A collection of widgets"""
from abc import ABC, abstractmethod
import pyglet
from typing import Callable

from ....utils import _hex_to_rgb
from ....config import SELECTED_COLOR, GRAY_COLOR, OTHER_COLOR

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

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool:
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

    def on_mouse_press(self, x, y, button, modifiers) -> bool:
        if self.hit_test(x, y):
            if self.action:
                self.action()
            return True
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







class Panel(Widget):
    """A container widget with a background"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 color: str = GRAY_COLOR,
                 anchor_top=False, anchor_right=False, anchor_bottom=False, anchor_left=False) -> None:
        super().__init__(x, y, width, height, anchor_top, anchor_right, anchor_bottom, anchor_left)
        self.color = color
        self.children: list[Widget] = []
        self._background: pyglet.shapes.Rectangle | None = None

    def add(self, widget: Widget) -> None:
        self.children.append(widget)

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        if self._background is None:
            self._background = pyglet.shapes.Rectangle(
                x=self.x, y=self.y,
                width=self.width, height=self.height,
                color=_hex_to_rgb(self.color),
                batch=batch
            )
        else:
            self._background.color = _hex_to_rgb(self.color)
            self._background.batch = batch

        for child in self.children:
            if child.visible:
                child.draw(batch)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool:
        for child in reversed(self.children):
            if child.hit_test(x, y) and child.on_mouse_press(x, y, button, modifiers):
                return True
        return False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool:
        for child in self.children:
            child.on_mouse_motion(x, y, dx, dy)
        return False

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self._on_reposition()
        for child in self.children:
            child.on_resize(width, height)

    def _on_reposition(self) -> None:
        if self._background:
            self._background.x = self.x
            self._background.y = self.y
            self._background.width = self.width
            self._background.height = self.height


class TabPanel(Panel):
    def __init__(self, x: int, y: int, width: int, height: int,
                 tab_height: int = 24,
                 color: str = GRAY_COLOR,
                 anchor_top=False, anchor_right=False, anchor_bottom=False, anchor_left=False) -> None:
        super().__init__(x, y, width, height, color, anchor_top, anchor_right, anchor_bottom, anchor_left)
        self.tab_height = tab_height
        self._tabs: dict[str, Panel] = {}
        self._active_tab: str | None = None
        self._tab_buttons: list[Button] = []

    def add_tab(self, name: str, panel: Panel) -> None:
        self._tabs[name] = panel
        if self._active_tab is None:
            self._active_tab = name

        tab_x = self.x + len(self._tab_buttons) * 80
        tab_y = self.y + self.height - self.tab_height
        self._tab_buttons.append(Button(
            x=tab_x, y=tab_y,
            width=80, height=self.tab_height,
            text=name,
            action=lambda n=name: setattr(self, '_active_tab', n),
            active=lambda n=name: self._active_tab == n
        ))

    def draw(self, batch: pyglet.graphics.Batch) -> None:
        super().draw(batch)
        for btn in self._tab_buttons:
            btn.draw(batch)
        if self._active_tab and self._active_tab in self._tabs:
            self._tabs[self._active_tab].draw(batch)

    def on_mouse_press(self, x, y, button, modifiers) -> bool:
        for btn in self._tab_buttons:
            if btn.on_mouse_press(x, y, button, modifiers):
                return True
        if self._active_tab:
            if self._tabs[self._active_tab].on_mouse_press(x, y, button, modifiers):
                return True
        return super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy) -> bool:
        for btn in self._tab_buttons:
            btn.on_mouse_motion(x, y, dx, dy)
        if self._active_tab:
            self._tabs[self._active_tab].on_mouse_motion(x, y, dx, dy)
        return False

    def on_resize(self, width, height) -> None:
        super().on_resize(width, height)
        # reposition tab buttons
        tab_x = self.x
        tab_y = self.y + self.height - self.tab_height
        for btn in self._tab_buttons:
            btn.x = tab_x
            btn.y = tab_y
            btn._on_reposition()
            tab_x += btn.width