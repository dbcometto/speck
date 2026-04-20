"""Establish systems that control dynamics"""
from .system import System
from ..components.dynamics import Position, Velocity
from ..core.world import World

class MovementSystem(System):
    """Acts on position and velocity components"""
    def update(self, world: World, dt: float):
        positions = world.get_component(Position)
        velocities = world.get_component(Velocity)

        for eid in positions.keys() & velocities.keys():
            positions[eid].x += velocities[eid].x * dt
            positions[eid].y += velocities[eid].y * dt
            positions[eid].z += velocities[eid].z * dt