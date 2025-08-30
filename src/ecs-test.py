# This is the beginning
import time
loop_period = 1
past_time = time.time()

# First, create components
class Position:
    def __init__(self,x,y):
        self.x = x
        self.y = y

class Velocity:
    def __init__(self,vx,vy):
        self.x = vx
        self.y = vy

class Radius:
    def __init__(self,radius):
        self.radius = radius


# Next, create entities
class Entity:
    def __init__(self,entity_id):
        self.id = entity_id
        self.components = {}

    def add_component(self, component):
        self.components[type(component)] = component

    def get(self, component_type):
        return self.components.get(component_type)
    

# Third, create systems

def system_movement(entities, dt):
    for e in entities:
        pos = e.get(Position)
        vel = e.get(Velocity)
        if pos and vel:
            pos.x += vel.x*dt
            pos.y += vel.y*dt


asteroid = Entity(1)
asteroid.add_component(Position(0,0))
asteroid.add_component(Velocity(1,0))
asteroid.add_component(Radius(1))


try:
    while True:
        current_time = time.time()

        if (current_time-past_time > loop_period):
            past_time = current_time

            entities = [asteroid]
            system_movement(entities, dt=1)
            
            for e in entities:
                print(f"Asteroid {e.id} is at ({e.get(Position).x},{e.get(Position).y})")

except KeyboardInterrupt:
    pass