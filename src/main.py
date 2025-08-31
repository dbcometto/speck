# This is the beginning
import time

from entities import Rock
from components import Position, Velocity, Acceleration, Radius, Forces
from systems import ForceSystem, MovementSystem, RenderSystem
from systems import GravitySystem



# Config
hz = 30
timewarp = 1
dt = 1/hz
world_size = 200

    

if __name__ == "__main__":
    past_time = 0

    # entity_list = [Asteroid(1,velocity=(1,1)), Asteroid(2,velocity=(1,0),component_forces={"test":(-0.5,0)})]
    entity_list = [Rock(1,position=(-50,-50),velocity=(20,0),mass=1e20,radius=10), Rock(2,position=(50,50),velocity=(-20,0),mass=1e20,radius=10)]
    system_list = [GravitySystem(),ForceSystem(),MovementSystem(dt*timewarp),RenderSystem(size=200)]

    try:
        while True:
            current_time = time.time()

            if (current_time-past_time > dt):
                past_time = current_time

                for system in system_list:
                    system.update(entity_list)
                
                for e in entity_list:
                    print(f"Rock {e.id}: {e.get(Forces).components}")

    except KeyboardInterrupt:
        pass