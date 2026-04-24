"""Defines the base script"""
from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from ..core import World
    from ..components.assemblies import Assembly, Part

class Script(ABC):
    """Base class for all behavior scripts"""

    @abstractmethod
    def update(self, eid: int, world: World, dt: float) -> dict[str, any]: # TODO: make limited context
        ...

    def get_part(self, eid: int, world: World, part_type: type[Part]) -> Part | None:
        """Helper to find a part of a given type in this entity's assembly"""
        assembly = world.get_component(Assembly)
        parts = world.get_component(part_type)
        if eid not in assembly:
            return None
        for part_eid in assembly[eid].parts:
            if part_eid in parts:
                return parts[part_eid]
        return None