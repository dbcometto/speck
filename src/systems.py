# Here systems are defined
import math
import random
import matplotlib.pyplot as plt
plt.ion()

from utils import calc_distance

from components import Position, Velocity, Acceleration, Forces
from components import Radius, Mass
from components import Thruster

from entities import Rock, Agent

class System:
    def update(self, entities, entities_by_id):
        raise NotImplementedError
    

# Dynamics

class DynamicsGroup(System):
    def __init__(self,dt,timewarp):
        self.dt = dt
        self.gravitySystem = GravitySystem()
        self.forceSystem = ForceSystem()
        self.movementSystem = MovementSystem(dt=self.dt*timewarp)

    def update(self, entities, entities_by_id):
        self.gravitySystem.update(entities,entities_by_id)
        self.forceSystem.update(entities,entities_by_id)
        self.movementSystem.update(entities,entities_by_id)


class MovementSystem(System):
    def __init__(self,dt):
        self.dt = dt

    def update(self,entities, entities_by_id):
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

    def update(self,entities, entities_by_id):
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

    def update(self,entities, entities_by_id):

        for i1,e1 in enumerate(entities):
            for e2 in entities[i1+1:]: #enumerate(entities[i1+1:],start=i1+1):
                    print(f"{e1.id} and {e2.id}")
                    pos1 = e1.get(Position)
                    pos2 = e2.get(Position)
                    m1 = e1.get(Mass).mass
                    m2 = e2.get(Mass).mass
                    forces1 = e1.get(Forces)
                    forces2 = e2.get(Forces)

                    d,(dx,dy),(ux,uy) = calc_distance(e1,e2)

                    f = self.G*m1*m2/(d**2 + self.epsilon**2)

                    fx = ux*f
                    fy = uy*f

                    forces1.components[f"Gravity from {e2.id}"] = (fx, fy)
                    forces2.components[f"Gravity from {e1.id}"] = (-fx, -fy)




# Functionality

class FunctionalityGroup(System):
    def __init__(self):
        self.thrusterSystem = ThrusterSystem()

    def update(self, entities, entities_by_id):
        self.thrusterSystem.update(entities,entities_by_id)



class ThrusterSystem(System):
    def __init__(self):
        pass

    def update(self, entities, entities_by_id):
        for e in entities:
            thruster = e.get(Thruster)
            forces = e.get(Forces)

            if thruster and forces:
                thrust_x = 1
                thrust_y = random.random()

                norm = math.sqrt(thrust_x**2 + thrust_y**2)

                thrust_x = thrust_x*thruster.max_thrust/norm
                thrust_y = thrust_y*thruster.max_thrust/norm

                forces.components[f"Thruster"] = (thrust_x,thrust_y)






# Visualization

class RenderSystem(System):
    def __init__(self,size=200):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-size//2, size//2)
        self.ax.set_ylim(-size//2, size//2)
        self.ax.set_aspect('equal', adjustable='box')
        self.fig.patch.set_facecolor('#090909')  # sets the figure background
        self.ax.set_facecolor('#090909')     # sets the axes (plot) background

    def update(self, entities, entities_by_id):
        for patch in self.ax.patches:
            patch.remove()  

        for e in entities:
            pos = e.get(Position)
            radius = e.get(Radius)

            if pos and radius and type(e)==Rock:
                circle = plt.Circle((pos.x, pos.y), radius.radius, color='#666666')
                self.ax.add_patch(circle)

            if pos and radius and type(e)==Agent:
                circle = plt.Rectangle((pos.x, pos.y), 2,2, color="#4EDAC2")
                self.ax.add_patch(circle)

        plt.draw()
        self.fig.canvas.flush_events()  # small pause to update plot