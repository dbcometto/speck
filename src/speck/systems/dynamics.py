"""Establish systems that control dynamics"""
import math

from .system import System
from ..components.dynamics import Position, Velocity, Acceleration, Attitude, AngularVelocity, AngularAcceleration
from ..components.dynamics import Mass, GravitySource, GravityConsumer
from ..core.world import World

from ..config import G

class MovementSystem(System):
    """Acts on position and velocity components"""
    def update(self, world: World, dt: float):
        """Integrates accelerations to velocities and velocities to positions"""
        positions = world.get_component(Position)
        velocities = world.get_component(Velocity)
        accelerations = world.get_component(Acceleration)

        for eid in velocities.keys() & accelerations.keys():
            velocities[eid].x += accelerations[eid].x * dt
            velocities[eid].y += accelerations[eid].y * dt
            velocities[eid].z += accelerations[eid].z * dt

        for eid in positions.keys() & velocities.keys():
            positions[eid].x += velocities[eid].x * dt
            positions[eid].y += velocities[eid].y * dt
            positions[eid].z += velocities[eid].z * dt
        
class ResetAccelerationSystem(System):
    """Reset the accelerations to 0"""
    def update(self, world: World, dt: float):
        accelerations = world.get_component(Acceleration)
        for eid in accelerations.keys():
            accelerations[eid].x = 0.0
            accelerations[eid].y = 0.0
            accelerations[eid].z = 0.0





class AttitudeSystem(System):
    """Integrates angular acceleration into angular velocity and attitude"""
    def update(self, world: World, dt: float):
        attitudes = world.get_component(Attitude)
        angular_velocities = world.get_component(AngularVelocity)
        angular_accelerations = world.get_component(AngularAcceleration)

        # integrate angular acceleration into angular velocity
        for eid in angular_velocities.keys() & angular_accelerations.keys():
            angular_velocities[eid].x += angular_accelerations[eid].x * dt
            angular_velocities[eid].y += angular_accelerations[eid].y * dt
            angular_velocities[eid].z += angular_accelerations[eid].z * dt

        # integrate angular velocity into attitude quaternion
        for eid in attitudes.keys() & angular_velocities.keys():
            q = attitudes[eid]
            w = angular_velocities[eid]

            # Apply exp map to get change in attitude from quaternion and euler integrate
            # q_dot = 0.5 * q (x) w_pure
            # w_pure = (0, wx, wy, wz)
            q_dot_w = 0.5 * (-q.x*w.x - q.y*w.y - q.z*w.z)
            q_dot_x = 0.5 * ( q.w*w.x + q.y*w.z - q.z*w.y)
            q_dot_y = 0.5 * ( q.w*w.y - q.x*w.z + q.z*w.x)
            q_dot_z = 0.5 * ( q.w*w.z + q.x*w.y - q.y*w.x)

            q.w += q_dot_w * dt
            q.x += q_dot_x * dt
            q.y += q_dot_y * dt
            q.z += q_dot_z * dt

            # normalize back onto SO(3) to maintain manifold constraint
            norm = (q.w**2 + q.x**2 + q.y**2 + q.z**2) ** 0.5
            if norm > 0:
                q.w /= norm
                q.x /= norm
                q.y /= norm
                q.z /= norm

        
        
class ResetAngularAccelerationSystem(System):
    """Reset the accelerations to 0"""
    def update(self, world: World, dt: float):
        angular_accelerations = world.get_component(AngularAcceleration)
        for eid in angular_accelerations.keys():
            angular_accelerations[eid].x = 0.0
            angular_accelerations[eid].y = 0.0
            angular_accelerations[eid].z = 0.0




class GravitySystem(System):
    """Runs gravity"""
    def update(self, world: World, dt: float):
        """Calculate gravity effects"""
        positions = world.get_component(Position)
        masses = world.get_component(Mass)
        accelerations = world.get_component(Acceleration)
        sources = world.get_component(GravitySource)
        consumers = world.get_component(GravityConsumer)

        source_eids = sources.keys() & positions.keys() & masses.keys()
        consumer_eids = consumers.keys() & positions.keys() & masses.keys() & accelerations.keys()

        for ceid in consumer_eids:
            ax, ay, az = self._compute_acceleration(ceid, source_eids, positions, masses)
            accelerations[ceid].x += ax
            accelerations[ceid].y += ay
            accelerations[ceid].z += az

    def _compute_acceleration(self, ceid, source_eids, positions, masses):
        ax, ay, az = 0.0, 0.0, 0.0
        for seid in source_eids:
            if seid == ceid:
                continue
            dx = positions[seid].x - positions[ceid].x
            dy = positions[seid].y - positions[ceid].y
            dz = positions[seid].z - positions[ceid].z
            dist = math.sqrt(dx**2 + dy**2 + dz**2)
            if dist == 0:
                continue
            a = G * masses[seid].mass / dist**2
            ax += a * dx / dist
            ay += a * dy / dist
            az += a * dz / dist
        return ax, ay, az
