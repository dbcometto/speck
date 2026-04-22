"""Run Speck"""
import pyglet

from speck.core import World
from speck.components.dynamics import Position, Velocity

from speck.renderer.windows import ViewportWindow, InspectorWindow
from speck.systems.dynamics import ResetAccelerationSystem, GravitySystem, MovementSystem

from speck.scenarios.base_scenarios import generate_scene_smallbody, generate_scene_2smallbody

import time


# Config
dt = 1/60
timewarp = 1.0


# Create a world
world = World(timewarp=timewarp)

# Systems in order
world.add_system(ResetAccelerationSystem())
world.add_system(GravitySystem())
world.add_system(MovementSystem())

# Populate the world
# generate_scene_smallbody(world)
generate_scene_2smallbody(world)

# Set up rendering
windows = []
main_window = ViewportWindow(world, windows, width=1800, height=900)






# define update
start = time.perf_counter()
def update(dt):
    world.update(dt)
    main_window.hud.update_ups(dt)

pyglet.clock.schedule_interval(update, dt)
pyglet.app.run()