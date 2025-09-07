# This code uses pyglet to render the game

import pyglet
from pyglet import shapes

from world import World


class SpeckWindow(pyglet.window.Window):

    def __init__(self, width=800, height=600):
        super().__init__(width, height, "Pyglet Class Example")
        self.batch = pyglet.graphics.Batch()
        self.circle = shapes.Circle(200, 300, 50, color=(50, 225, 30), batch=self.batch)

        pyglet.clock.schedule_interval(self.update, 1/60.0)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def update(self, dt):
        self.circle.x += 100 * dt
        if self.circle.x > self.width + self.circle.radius:
            self.circle.x = -self.circle.radius

    def on_key_press(self, symbol, modifiers):
        print(f"Key pressed: {symbol}")

# Run the app
if __name__ == "__main__":
    window = SpeckWindow()
    pyglet.app.run()
