import pyglet
from pyglet import shapes

# Create window
window = pyglet.window.Window(800, 600, "Pyglet Example")

# Create a batch for efficient drawing
batch = pyglet.graphics.Batch()

# Shapes
circle = shapes.Circle(200, 300, 50, color=(50, 225, 30), batch=batch)
square = shapes.Rectangle(400, 300, 100, 100, color=(200, 30, 30), batch=batch)

# Input handlers
@window.event
def on_key_press(symbol, modifiers):
    print(f"Key pressed: {symbol}")

@window.event
def on_mouse_press(x, y, button, modifiers):
    print(f"Mouse pressed at ({x}, {y})")

# Animation/update
def update(dt):
    circle.x += 100 * dt  # move circle right at 100 px/sec
    if circle.x > window.width + circle.radius:
        circle.x = -circle.radius  # wrap around

pyglet.clock.schedule_interval(update, 1/60.0)  # 60 FPS

# Draw loop
@window.event
def on_draw():
    window.clear()
    batch.draw()

# Run the app
pyglet.app.run()
