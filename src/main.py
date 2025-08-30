# This is the beginning
import time

from entities import Asteroid
from components import Position, Velocity, Radius
from systems import ForceSystem, MovementSystem, RenderSystem



# Config
dt = 1
world_size = 200

    

if __name__ == "__main__":
    past_time = 0

    entity_list = [Asteroid(1,velocity=(1,1)), Asteroid(2,velocity=(1,0),component_forces={"test":(-0.5,0)})]
    system_list = [ForceSystem(),MovementSystem(dt),RenderSystem(size=200)]

    try:
        while True:
            current_time = time.time()

            if (current_time-past_time > dt):
                past_time = current_time

                for system in system_list:
                    system.update(entity_list)
                
                for e in entity_list:
                    print(f"Asteroid {e.id} is at ({e.get(Position).x},{e.get(Position).y})")

    except KeyboardInterrupt:
        pass