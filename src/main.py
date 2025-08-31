# This is the beginning
import time

from entities import Rock
from components import Position, Velocity, Acceleration, Radius, Forces
from systems import ForceSystem, MovementSystem, RenderSystem
from systems import DynamicsGroup



# Config
hz = 30
timewarp = 1
dt = 1/hz
world_size = 200

    

if __name__ == "__main__":
    past_time = 0

    # entity_list = [Asteroid(1,velocity=(1,1)), Asteroid(2,velocity=(1,0),component_forces={"test":(-0.5,0)})]
    entity_list = [Rock(1,position=(0,0),velocity=(0,0),mass=1e21,radius=10), Rock(2,position=(0,-50),velocity=(40,0),mass=1e5,radius=5)]
    system_list = [DynamicsGroup(dt=dt,timewarp=timewarp),RenderSystem(size=200)]

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