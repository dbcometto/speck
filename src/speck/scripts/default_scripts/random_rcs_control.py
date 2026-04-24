"""Defines a script that outputs random control commands"""
from ..script import Script

import random


class RandomRCSControl(Script):
    """Randomly outputs thruster control commands"""

    def update(self, *args, **kwargs) -> dict[str, any]:
        """Set a random thrust to port `out`"""
        random_value = random.uniform(-1,1)
        return {"out": random_value}
