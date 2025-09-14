# This is the beginning
import time
import math
import random

# Fix ctrl-c issues with matplotlib
import signal, sys
signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))

from .entities import Entity
from .world import World
from .components import Behavior_Orbiter, RenderData
from .config import G

from .factories import create_rock, create_agent

    

if __name__ == "__main__":

    fred = create_agent(3,position=(500,0),velocity=(0,20),mass=1,max_thrust=50,radius=3)
    fred.add_component(Behavior_Orbiter(1, orbit_distance=800))

    bob = create_agent(4,position=(-60,),velocity=(10,-10),mass=1,max_thrust=50,radius=3)
    # bob.add_component(Behavior_Orbiter(2, orbit_distance=15))

    entity_list = [
        create_rock(1,position=(0,0),velocity=(0,0),mass=9e17,radius=473), 
        create_rock(2,position=(0,-1000),velocity=(math.sqrt(G*9e17/1000),0),mass=1e8,radius=20),
        create_rock(5,position=(0,600),velocity=(0,0),mass=1e4,radius=10),
        fred,
        bob,
        ]

    # Add dust
    num_particles = 800
    ring_radius = 500
    fudge = 20

    for i in range(num_particles):
        r = create_rock(
                6+i,
                position=(
                    ring_radius * math.cos(2 * math.pi * i / num_particles) + fudge*random.uniform(-1,1),
                    ring_radius * math.sin(2 * math.pi * i / num_particles) + fudge*random.uniform(-1,1)
                ),
                velocity=(0, 0),
                mass=1e2,
                radius=4
            )
        r.add_component(RenderData(color="#22FFFF"))
        entity_list.append(r)

    # World Creation and Spinning

    world = World(entitylist=entity_list,hz=60,render_hz=60,timewarp=10)

    # world = World(hz=60,render_hz=60,timewarp=1)
    # world.generate(boundary=5000,max_rocks=800)

    # world = World(worldpath="worlds/physics_test_world.json",timewarp=1,hz=60)
    # world.load()

    print("Spinning up the world!")

    world.spin(debugging=True)






    # Past Entity Lists

    # entity_list = [Asteroid(1,velocity=(1,1)), Asteroid(2,velocity=(1,0),component_forces={"test":(-0.5,0)})] # This one is for ForceSystem and MovementSystem



    # entity_list = [Rock(1,position=(0,0),velocity=(0,0),mass=1e21,radius=10), Rock(2,position=(0,-50),velocity=(40,0),mass=1e5,radius=5)] # This one is for GravitySystem




    # fred = Agent(3,position=(60,0),velocity=(0,20),mass=1,max_thrust=50,width=3)
    # fred.add_component(Behavior_Orbiter(1, orbit_distance=50))

    # entity_list = [
    #     Rock(1,position=(0,0),velocity=(0,0),mass=1e21,radius=10), 
    #     Rock(2,position=(0,-50),velocity=(40,0),mass=1e5,radius=5),
    #     fred,
    #     bob,
    #     ]
    



    # fred = Agent(3,position=(60,0),velocity=(0,20),mass=1,max_thrust=50,width=3)
    # fred.add_component(Behavior_Orbiter(1, orbit_distance=50))

    # bob = Agent(4,position=(-60,),velocity=(10,-10),mass=1,max_thrust=50,width=3)
    # # bob.add_component(Behavior_Orbiter(2, orbit_distance=15))

    # entity_list = [
    #     Rock(1,position=(0,0),velocity=(0,0),mass=1e21,radius=10), 
    #     Rock(2,position=(0,-50),velocity=(40,0),mass=1e5,radius=5),
    #     Rock(4,position=(0,50),velocity=(-10,0),mass=1,radius=1),
    #     fred,
    #     bob,
    #     ]
