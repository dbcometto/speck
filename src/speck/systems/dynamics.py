"""Establish systems that control dynamics"""
import math

from .system import System
from ..components.dynamics import Position, Velocity, Acceleration
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
    """Acts on acceleration components"""
    def update(self, world: World, dt: float):
        """Resets accelerations to zero"""
        accelerations = world.get_component(Acceleration)

        for eid in accelerations.keys():
            accelerations[eid].x = 0.0
            accelerations[eid].y = 0.0
            accelerations[eid].z = 0.0



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
