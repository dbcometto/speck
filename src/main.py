# This is the beginning
import time

from entities import Asteroid
from components import Position, Velocity, Radius
from systems import MovementSystem



dt = 1
past_time = 0
    

if __name__ == "__main__":

    entity_list = [Asteroid(1,(0,0),(1,0),1), Asteroid(2,(0.1,0),(1,0.25),1)]
    system_list = [MovementSystem()]

    try:
        while True:
            current_time = time.time()

            if (current_time-past_time > dt):
                past_time = current_time

                for system in system_list:
                    system.update(entity_list, dt)
                
                for e in entity_list:
                    print(f"Asteroid {e.id} is at ({e.get(Position).x},{e.get(Position).y})")

    except KeyboardInterrupt:
        pass