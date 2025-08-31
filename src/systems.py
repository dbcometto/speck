# Here systems are defined
import math
import random

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
plt.ion()

from utils import calc_distance
from config import G

from components import Position, Velocity, Acceleration, Forces
from components import Radius, Mass, Width
from components import Thruster
from components import Behavior_Orbiter, Behavior_RandomThruster

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
        self.G = G                                # in MN km^2/t^2
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
            behaviorRandom = e.get(Behavior_RandomThruster)

            if thruster and forces:

                if behaviorRandom:
                    thrust_x = random.random()-0.5
                    thrust_y = random.random()-0.5
                else:
                    thrust_x = thruster.desired_thrust_x
                    thrust_y = thruster.desired_thrust_y

                norm = math.sqrt(thrust_x**2 + thrust_y**2)

                if norm != 0:
                    thruster.thrust_x = thrust_x/norm*thruster.max_thrust*thruster.throttle
                    thruster.thrust_y = thrust_y/norm*thruster.max_thrust*thruster.throttle

                    forces.components[f"Thruster"] = (thruster.thrust_x,thruster.thrust_y)


# Behavior Group

class BehaviorGroup(System):
    def __init__(self):
        self.simpleOrbiterSystem = SimpleOrbiterSystem()

    def update(self, entities, entities_by_id):
        self.simpleOrbiterSystem.update(entities,entities_by_id)



class SimpleOrbiterSystem(System):
    def __init__(self):
        self.G = G
        self.kp = 5

    def update(self, entities, entities_by_id):
        for e in entities:
            thruster = e.get(Thruster)
            forces = e.get(Forces)
            vel = e.get(Velocity)
            behaviorOrbiter = e.get(Behavior_Orbiter)

            

            if behaviorOrbiter and forces and thruster and vel:
                eO = entities_by_id[behaviorOrbiter.orbit_id]
                M = eO.get(Mass)

                if M:
                    d,(dx,dy),(ux,uy) = calc_distance(e,eO)

                    v_needed = math.sqrt(self.G*M.mass/d)
                    v_needed_x = -dy/d*v_needed
                    v_needed_y = dx/d*v_needed

                    thruster.throttle = 1

                    error_x = v_needed_x - vel.x
                    error_y = v_needed_y - vel.y

                    if error_x + error_y > behaviorOrbiter.vel_tolerance:

                        thrust_needed_x = self.kp*error_x
                        thrust_needed_y = self.kp*error_y

                        thruster.desired_thrust_x = -thrust_needed_x
                        thruster.desired_thrust_y = -thrust_needed_y








# Visualization

class RenderGroup(System):
    def __init__(self,size=200):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-size//2, size//2)
        self.ax.set_ylim(-size//2, size//2)
        self.ax.set_aspect('equal', adjustable='box')
        self.fig.patch.set_facecolor('#090909')  # sets the figure background
        self.ax.set_facecolor('#090909')     # sets the axes (plot) background

        self.renderSystem = RenderSystem(self.fig,self.ax)

    def update(self, entities, entities_by_id):
        self.renderSystem.update(entities,entities_by_id)


class RenderSystem(System):
    def __init__(self,fig,ax):
        self.fig = fig
        self.ax = ax

        self.thruster_scale = 1.3
        self.thruster_width = 1.8
        

    def update(self, entities, entities_by_id):
        for patch in self.ax.patches:
            patch.remove()  

        for e in entities:
            pos = e.get(Position)
            radius = e.get(Radius)
            width = e.get(Width)
            width = width.width if width else None

            thruster = e.get(Thruster)

            if pos and radius and type(e)==Rock:
                circle = plt.Circle((pos.x, pos.y), radius.radius, color='#666666')
                self.ax.add_patch(circle)

            if pos and width and type(e)==Agent:
                if thruster:
                    arrow = FancyArrowPatch((pos.x, pos.y), (pos.x - thruster.thrust_x*self.thruster_scale, pos.y - thruster.thrust_y*self.thruster_scale), arrowstyle='-', mutation_scale=100, color="#FF7038", linewidth=self.thruster_width)
                    self.ax.add_patch(arrow)

                circle = plt.Rectangle((pos.x-width/2, pos.y-width/2), width,width, color="#4EDAC2")
                self.ax.add_patch(circle)

                


        plt.draw()
        self.fig.canvas.flush_events()  # small pause to update plot