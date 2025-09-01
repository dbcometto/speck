# This is the beginning
import time

# Fix ctrl-c issues with matplotlib
import signal, sys
signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))

from entities import Rock, Agent
from world import World
from components import Behavior_Orbiter

    

if __name__ == "__main__":
    # Config
    hz = 30
    timewarp = 1
    dt = 1/hz
    world_size = 200

    fred = Agent(3,position=(60,0),velocity=(0,20),mass=1,max_thrust=50,width=3)
    fred.add_component(Behavior_Orbiter(1, orbit_distance=50))

    entity_list = [
        Rock(1,position=(0,0),velocity=(0,0),mass=1e21,radius=10), 
        Rock(2,position=(0,-50),velocity=(40,0),mass=1e5,radius=5),
        fred,
        ]



    # World Creation and Spinning

    world = World(entitylist=entity_list)

    world.spin(debugging=True)






    # Past Entity Lists

    # entity_list = [Asteroid(1,velocity=(1,1)), Asteroid(2,velocity=(1,0),component_forces={"test":(-0.5,0)})] # This one is for ForceSystem and MovementSystem
    # entity_list = [Rock(1,position=(0,0),velocity=(0,0),mass=1e21,radius=10), Rock(2,position=(0,-50),velocity=(40,0),mass=1e5,radius=5)] # This one is for GravitySystem
    
    
