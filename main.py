"""Run Speck"""
import pyglet

from speck.core import World
from speck.renderer.windows import ViewportWindow, InspectorWindow
from speck.systems.dynamics import ResetAccelerationSystem, ResetAngularAccelerationSystem, GravitySystem, MovementSystem, AttitudeSystem
from speck.systems.assemblies import AssemblySystem

from speck.scenarios.base_scenarios import generate_scene_smallbody, generate_scene_2smallbody
from speck.scenarios.agent_scenarios import generate_scene_emptythruster, generate_scene_emptythrusterrcs

import time


# Config
dt = 1/60
timewarp = 1


# Create a world
world = World(timewarp=timewarp, debug_prints=False)

# Systems in order
world.add_system(ResetAccelerationSystem())
world.add_system(ResetAngularAccelerationSystem())
world.add_system(GravitySystem())
world.add_system(AssemblySystem())
world.add_system(MovementSystem())
world.add_system(AttitudeSystem())

# Populate the world
# generate_scene_smallbody(world)
# generate_scene_2smallbody(world)
generate_scene_emptythrusterrcs(world)

# Set up rendering
windows = []
main_window = ViewportWindow(world, windows, width=1800, height=900)
# main_window2 = ViewportWindow(world, windows, width=1800, height=900)






# define update
start = time.perf_counter()
def update(dt):
    world.update(dt)
    main_window.hud.update_ups(dt)

pyglet.clock.schedule_interval(update, dt)
pyglet.app.run()