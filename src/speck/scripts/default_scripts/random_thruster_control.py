"""Defines a script that outputs random control commands"""
from ..script import Script

import random


class RandomThrusterControl(Script):
    """Randomly outputs thruster control commands"""

    def update(self, *args, **kwargs) -> dict[str, any]:
        """Set a random thrust to port `out`"""
        random_value = random.random()
        return {"out": random_value}
