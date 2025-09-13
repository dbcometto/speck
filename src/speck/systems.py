# Here systems are defined
import math

from .utils import calc_distance
from .config import G, mass_unit_factor

from .components import Position, Velocity, Acceleration, Forces
from .components import Radius, Mass
from .components import Thruster
from .components import Behavior_Orbiter
from .components import RenderData

from .entities import Entity

from .barnes_hut import QuadNode, compute_force

class System:
    def update(self, entities, entities_by_id):
        raise NotImplementedError
    

# Dynamics

class DynamicsGroup(System):
    def __init__(self,dt,timewarp):
        self.dt = dt
        self.systems = [
            GravitySystem(),
            ForceSystem(),
            MovementSystem(dt=self.dt*timewarp),
            CollisionSystem()
        ]
        

    def update(self, entities, entities_by_id):
        
        for system in self.systems:
            system.update(entities,entities_by_id)
        


class MovementSystem(System):
    def __init__(self,dt=1):
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
        self.epsilon = 0.1

    def update(self,entities, entities_by_id):

        for e in entities:
            forces = e.get(Forces)
            if forces:
                forces.components["Gravity"] = (0.0, 0.0)

        positions = [e.get(Position) for e in entities if e.has(Position)]
        if not positions:
            return

        x_min = min(p.x for p in positions)
        x_max = max(p.x for p in positions)
        y_min = min(p.y for p in positions)
        y_max = max(p.y for p in positions)
        root = QuadNode(x_min, x_max, y_min, y_max)
        for e in entities:
            root.insert(e)

        # Compute forces
        for e in entities:
            compute_force(e, root, G=G, theta=0.5, eps=self.epsilon)

        # # O(n^2)
        # for i1,e1 in enumerate(entities):
        #     for e2 in entities[i1+1:]: #enumerate(entities[i1+1:],start=i1+1):
        #             m1 = e1.get(Mass).mass
        #             m2 = e2.get(Mass).mass
        #             forces1 = e1.get(Forces)
        #             forces2 = e2.get(Forces)

        #             d,(dx,dy),(ux,uy) = calc_distance(e1,e2)

        #             f = config.G*m1*m2/(d**2 + self.epsilon**2)

        #             fx = ux*f
        #             fy = uy*f

        #             forces1.components[f"Gravity from {e2.id}"] = (fx, fy)
        #             forces2.components[f"Gravity from {e1.id}"] = (-fx, -fy)


class CollisionSystem:
    def __init__(self,restitution=0.5,friction_coeff=0.7):
        self.restitution = restitution
        self.friction_coeff = friction_coeff

    def update(self,entities, entities_by_id):
        """Apply 2D elastic collisions between rocks and rocks or agents and rocks"""
        for i1,e1 in enumerate(entities):
            for e2 in entities[i1+1:]:
                    # print(f"Checking collision between {e1.id} and {e2.id}")
                    # if not (type(e1)==Agent and type(e2)==Agent):
                    m1 = e1.get(Mass)
                    m2 = e2.get(Mass)
                    v1 = e1.get(Velocity)
                    v2 = e2.get(Velocity)
                    r1 = e1.get(Radius)
                    r2 = e2.get(Radius)
                    pos1 = e1.get(Position)
                    pos2 = e2.get(Position)


                    if all([m1, m2, v1, v2, r1, r2, pos1, pos2]):

                        m1 = m1.mass * mass_unit_factor
                        m2 = m2.mass * mass_unit_factor
                        r1 = r1.radius
                        r2 = r2.radius

                        d,(dx,dy),(unx,uny) = calc_distance(e1,e2)
                        utx,uty = -uny,unx

                        d_min = r2+r1
                        if d <= d_min:
                            # clamp positions by mass
                            total_mass = m1 + m2
                            overlap = d_min-d
                            pos1.x -= unx * overlap * (m2 / total_mass)
                            pos1.y -= uny * overlap * (m2 / total_mass)
                            pos2.x += unx * overlap * (m1 / total_mass)
                            pos2.y += uny * overlap * (m1 / total_mass)

                            # Elastic collision
                            v_rel = (v1.x - v2.x)*unx + (v1.y - v2.y)*uny
                            impulse = ((self.restitution+1) * v_rel) / (1/m1 + 1/m2)

                            v1.x -= (impulse / m1) * unx
                            v1.y -= (impulse / m1) * uny
                            v2.x += (impulse / m2) * unx
                            v2.y += (impulse / m2) * uny

                            # Some friction
                            v1_tangent = v1.x*utx + v1.y*uty
                            v2_tangent = v2.x*utx + v2.y*uty
                            v1.x -= v1_tangent*utx*self.friction_coeff
                            v1.y -= v1_tangent*uty*self.friction_coeff
                            v2.x -= v2_tangent*utx*self.friction_coeff
                            v2.y -= v2_tangent*uty*self.friction_coeff

                            # print(f"{time.time()}: Collision between {e1.id} and {e2.id} with overlap {overlap:4.2f} | New v1 ({v1.x:4.2f},{v1.y:4.2f}) and v2 ({v2.x:4.2f},{v2.y:4.2f}) | \nNew distance {calc_distance(e1,e2)[0]:4.2f}")
                                


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

        self.kpt = 1
        self.kpr = 0.2

    def update(self, entities, entities_by_id):
        for e in entities:
            thruster = e.get(Thruster)
            forces = e.get(Forces)
            vel = e.get(Velocity)
            behaviorOrbiter = e.get(Behavior_Orbiter)

            

            if behaviorOrbiter and forces and thruster and vel:
                eO = entities_by_id[behaviorOrbiter.orbit_id]
                M = eO.get(Mass)
                
                mass = e.get(Mass)
                mass = mass.mass if mass else None

                d_desired = behaviorOrbiter.orbit_distance

                if M and mass:
                    d,(dx,dy),(ux,uy) = calc_distance(eO,e)
                    
                    # make unit vectors
                    urx,ury = ux,uy
                    utx,uty = -ury,urx

                    # calculate desired circular velocity
                    v_needed = math.sqrt(G*M.mass/d_desired)

                    # calculate current velocity in terms of r/t frame
                    vr = vel.x * urx + vel.y * ury
                    vt = vel.x * utx + vel.y * uty

                    # radial controller
                    error_r = d_desired - d
                    ar = self.kpr*error_r

                    # tangential controller
                    vt_needed = v_needed
                    error_vt = vt_needed - vt
                    at = self.kpt*error_vt

                    # Calculate forces
                    Fr = mass*ar
                    Ft = mass*at

                    # Change coords back
                    Fx = Fr*urx + Ft*utx
                    Fy = Fr*ury + Ft*uty
                    Fmag = math.hypot(Fx**2+Fy**2)

                    thruster.throttle = min(1.0, Fmag/thruster.max_thrust if thruster.max_thrust > 0 else 0)
                    thruster.desired_thrust_x = Fx/Fmag if Fmag > 0 else 0
                    thruster.desired_thrust_y = Fy/Fmag if Fmag > 0 else 0

                    # print(f"d: {d:4.2f} | vt: {vt:4.2f} | verror: {error_vt:4.2f}")








