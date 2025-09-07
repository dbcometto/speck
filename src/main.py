# This is the beginning
import time
import math

# Fix ctrl-c issues with matplotlib
import signal, sys
signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))

from entities import Rock, Agent
from world import World
from components import Behavior_Orbiter
import config

    

if __name__ == "__main__":

    fred = Agent(3,position=(500,0),velocity=(0,20),mass=1,max_thrust=50,width=3)
    fred.add_component(Behavior_Orbiter(1, orbit_distance=800))

    bob = Agent(4,position=(-60,),velocity=(10,-10),mass=1,max_thrust=50,width=3)
    # bob.add_component(Behavior_Orbiter(2, orbit_distance=15))

    entity_list = [
        Rock(1,position=(0,0),velocity=(0,0),mass=9e17,radius=473), 
        Rock(2,position=(0,-1000),velocity=(math.sqrt(config.G*9e17/1000),0),mass=1e5,radius=5),
        fred,
        bob,
        ]



    # World Creation and Spinning

    world = World(entitylist=entity_list,hz=60,render_hz=60)

    # world = World()
    # world.generate()

    # world = World(worldpath="worlds/physics_test_world.json",timewarp=0.001,hz=600)
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
