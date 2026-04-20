"""Run Speck"""
import pyglet

from speck.core import World
from speck.components.dynamics import Position, Velocity

from speck.renderer import PygletRenderer2D, Camera, InputHandler, HUD
from speck.systems.dynamics import ResetAccelerationSystem, GravitySystem, MovementSystem

from speck.scenarios.base_scenarios import generate_scene_smallbody, generate_scene_2smallbody

import time


# Config
dt = 1/60
timewarp = 3600.0*24

end_timewarp = 10.0
end_time = 10.0


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
camera = Camera()
hud = HUD(world, camera)
renderer = PygletRenderer2D(world, camera, hud)

# Set up input
input_handler = InputHandler(camera)
renderer.window.push_handlers(input_handler)






# define update
start = time.perf_counter()
def update(dt):
    world.update(dt)
    hud.update_ups(dt)

    # Testing time warp schedule
    if time.perf_counter()-start >= end_time:
        world.timewarp = end_timewarp

    # Debugging:
    # positions = world.get_component(Position)
    # for eid, pos in positions.items():
    #     print(f"eid={eid} x={pos.x:.4f} y={pos.y:.4f}")

pyglet.clock.schedule_interval(update, dt)
pyglet.app.run()