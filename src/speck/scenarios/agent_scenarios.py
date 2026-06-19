"""Define scenarios using the agent SDK"""
from speck.core import World

from speck.sdk.agent import Agent
from speck.sdk.parts import Thruster, Tank, Computer, AttitudeController
import random


class ThrusterTestAgent(Agent):
    def define(self):
        # Add parts
        tank     = self.add(Tank("fuel", capacity=1000.0, fill=1000.0))
        thruster = self.add(Thruster(max_thrust=1.0))
        cpu      = self.add(Computer(outputs=["throttle_out"]))

        # Connect parts
        self.connect(tank.fuel_out,       thruster.fuel_in)
        self.connect(cpu.throttle_out,    thruster.throttle_in)

        # Add scripts
        cpu.run(self.control, period=1.0)

    def control(self, world, dt):
        return {"throttle_out": random.uniform(0, 1)}


class ThrusterRCSTestAgent(Agent):
    def define(self):
        # Add parts
        tank     = self.add(Tank("fuel", capacity=1000.0, fill=1000.0))
        thruster = self.add(Thruster(max_thrust=1.0))
        rcs      = self.add(AttitudeController(max_torque=1.0))
        cpu      = self.add(Computer(outputs=["throttle_out", "attitude_out"]))

        # Connect parts
        self.connect(tank.fuel_out,       thruster.fuel_in)
        self.connect(cpu.throttle_out,    thruster.throttle_in)
        self.connect(cpu.attitude_out,    rcs.control_in)

        # Add scripts
        cpu.run(self.control, period=1.0)

    def control(self, world, dt):
        return {
            "throttle_out": random.uniform(0, 1),
            "attitude_out": random.uniform(-1, 1)
        }


def generate_scene_emptythruster(world: World):
    world.spawn(ThrusterTestAgent, mass=1)

def generate_scene_emptythrusterrcs(world: World):
    world.spawn(ThrusterRCSTestAgent, mass=1)