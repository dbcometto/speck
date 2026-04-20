"""Base systems"""
from abc import ABC, abstractmethod
from ..core import World


class System(ABC):
    """A base system"""
    @abstractmethod
    def update(self, world: World, dt):
        pass