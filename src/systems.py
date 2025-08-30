# Here systems are defined

from components import Position, Velocity, Radius

class System:
    def update(self, entities, dt):
        raise NotImplementedError


class MovementSystem(System):
    def update(self,entities,dt):
        for e in entities:
            pos = e.get(Position)
            vel = e.get(Velocity)
            if pos and vel:
                pos.x += vel.x*dt
                pos.y += vel.y*dt