# Here systems are defined
import math
import matplotlib.pyplot as plt
plt.ion()

from components import Position, Velocity, Acceleration, Forces
from components import Radius, Mass

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
            forces = e.get(Forces)
            mass = e.get(Mass)
            
            if acc and forces and mass:
                acc.x = forces.total_x/mass.mass
                acc.y = forces.total_y/mass.mass

            if vel and acc:
                vel.x += acc.x*self.dt
                vel.y += acc.y*self.dt
            
            if pos and vel:
                pos.x += vel.x*self.dt
                pos.y += vel.y*self.dt


class ForceSystem(System):
    def __init__(self):
        pass

    def update(self,entities):
        for e in entities:
            forces = e.get(Forces)

            if forces:
                forces.total_x = 0
                forces.total_y = 0

                for fx,fy in forces.components.values():
                    forces.total_x += fx
                    forces.total_y += fy

            

class GravitySystem:
    def __init__(self):
        self.G = (6.67e-17)                                 # in MN km^2/t^2
        self.epsilon = 1e-15

    def update(self,entities):

        for i1,e1 in enumerate(entities):
            for e2 in entities[i1+1:]: #enumerate(entities[i1+1:],start=i1+1):
                    print(f"{e1.id} and {e2.id}")
                    pos1 = e1.get(Position)
                    pos2 = e2.get(Position)
                    m1 = e1.get(Mass).mass
                    m2 = e2.get(Mass).mass
                    forces1 = e1.get(Forces)
                    forces2 = e2.get(Forces)

                    dx = pos2.x - pos1.x
                    dy = pos2.y - pos1.y

                    d = math.sqrt(dx**2+dy**2)

                    f = self.G*m1*m2/(d**2 + self.epsilon**2)

                    fx = dx/d*f
                    fy = dy/d*f

                    forces1.components[f"Gravity from {e2.id}"] = (fx, fy)
                    forces2.components[f"Gravity from {e1.id}"] = (-fx, -fy)








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