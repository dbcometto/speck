# This is the beginning
import time

from entities import Rock, Agent
from world import World

    

if __name__ == "__main__":
    # Config
    hz = 30
    timewarp = 1
    dt = 1/hz
    world_size = 200

    entity_list = [
        Rock(1,position=(0,0),velocity=(0,0),mass=1e21,radius=10), 
        Rock(2,position=(0,-50),velocity=(40,0),mass=1e5,radius=5),
        Agent(3,position=(50,0),velocity=(0,40),mass=1,max_thrust=5,width=3),
        ]



    # World Creation and Spinning

    world = World(entitylist=entity_list)

    world.spin(debugging=True)






    # Past Entity Lists

    # entity_list = [Asteroid(1,velocity=(1,1)), Asteroid(2,velocity=(1,0),component_forces={"test":(-0.5,0)})] # This one is for ForceSystem and MovementSystem
    # entity_list = [Rock(1,position=(0,0),velocity=(0,0),mass=1e21,radius=10), Rock(2,position=(0,-50),velocity=(40,0),mass=1e5,radius=5)] # This one is for GravitySystem
    
    
