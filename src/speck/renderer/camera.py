"""A camera"""

class Camera():
    """A Camera"""
    def __init__(self, width: int = 800, height: int = 600):
        """Init a Camera"""
        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0

        self.width = width
        self.height = height

        self.origin_x = 0.0
        self.origin_y = 0.0

    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        sx = (wx - self.x - self.origin_x) * self.zoom + self.width / 2
        sy = (wy - self.y - self.origin_y) * self.zoom + self.height / 2
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        wx = (sx - self.width / 2) / self.zoom + self.x + self.origin_x
        wy = (sy - self.height / 2) / self.zoom + self.y + self.origin_y
        return wx, wy
    

    # Pyglet Handlers
    def on_resize(self, width, height):
        self.width = width
        self.height = height
