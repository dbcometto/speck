"""Run Speck"""
import pyglet

from speck.core import World
from speck.components.dynamics import Position, Velocity

from speck.renderer import PygletRenderer2D, Camera, InputHandler, HUD
from speck.systems.dynamics import MovementSystem


# Config
dt = 1/60


# Create a world
world = World()

# Set up rendering
camera = Camera()
hud = HUD(world, camera)
renderer = PygletRenderer2D(world, camera, hud)

# Set up input
input_handler = InputHandler(camera)
renderer.window.push_handlers(input_handler)



# Create an entity
new_eid = world.create_entity()
position_component = Position()
world.add_component(new_eid, position_component)
velocity_component = Velocity(1)
world.add_component(new_eid, velocity_component)
world.add_system(MovementSystem())


# define update
def update(dt):
    world.update(dt)
    hud.update_ups(dt)

pyglet.clock.schedule_interval(update, dt)
pyglet.app.run()