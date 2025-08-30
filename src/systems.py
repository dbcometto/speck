# Here systems are defined
import matplotlib.pyplot as plt
plt.ion()

from components import Position, Velocity, Acceleration
from components import Radius

class System:
    def update(self, entities):
        raise NotImplementedError


class MovementSystem(System):
    def __init__(self,dt):
        self.dt = dt

    def update(self,entities):
        for e in entities:
            pos = e.get(Position)
            vel = e.get(Velocity)
            acc = e.get(Acceleration)
            
            if vel and acc:
                vel.x += acc.x*self.dt
                vel.y += acc.y*self.dt
            
            if pos and vel:
                pos.x += vel.x*self.dt
                pos.y += vel.y*self.dt



class RenderSystem(System):
    def __init__(self,size=200):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-size//2, size//2)
        self.ax.set_ylim(-size//2, size//2)
        self.ax.set_aspect('equal', adjustable='box')

    def update(self, entities):
        for patch in self.ax.patches:
            patch.remove()  

        for e in entities:
            pos = e.get(Position)
            radius = e.get(Radius)
            if pos and radius:
                circle = plt.Circle((pos.x, pos.y), radius.radius, color='gray')
                self.ax.add_patch(circle)

        plt.draw()
        self.fig.canvas.flush_events()  # small pause to update plot