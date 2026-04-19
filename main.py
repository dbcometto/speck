"""Run Speck"""
import pyglet

from speck.core import World
from speck.components.dynamics import Position

from speck.renderer import PygletRenderer2D, Camera, InputHandler


# Create a world
world = World()

# Set up rendering
camera = Camera()
renderer = PygletRenderer2D(world, camera)

# Set up input
input_handler = InputHandler(camera)
renderer.window.push_handlers(input_handler)

# Create an entity
new_eid = world.create_entity()
position_component = Position()
world.add_component(new_eid, position_component)

pyglet.app.run()