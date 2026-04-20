"""Define some predefined scenarios"""
import math

from speck.core import World
from speck.entities import generate_body, generate_moveable_agent

from speck.config import G






# Scenarios 

def generate_scene_almostempty(world: World):
    """Populate the world with one moveable agent"""
    generate_moveable_agent(world, vx = 1)


def generate_scene_smallbody(world: World, bodymass = 1e18, r=13.5, agentmass = 1e3, radius = 5):
    """Populate the world with an agent orbiting a small body"""
    # Add a body to the origin
    generate_body(world, mass=bodymass)

    # Add an agent in a circular orbit
    v = math.sqrt(G*bodymass/r)
    generate_moveable_agent(world, x = r, vy = v, mass=agentmass)

    print(f"Body set to orbit at r = {r} km with v = {v} km/s")



def generate_scene_2smallbody(world: World, x1 = 0, m1 = 1e22, m2 = 1e20, r=500.0, ra = 10.0, agentmass = 1e3, radius1 = 20, radius2 = 5):
    """Populate the world with a body orbiting a body and an agent around the second body"""
    # Add two main bodies
    com_x = (m1*x1 + m2 * (x1+r)) / (m1 + m2)
    v1 = -math.sqrt(G*m2**2 / (r*(m1+m2)))
    v2 = math.sqrt(G*m1**2 / (r*(m1+m2)))

    generate_body(world, x = x1, mass=m1, vy = v1, radius=radius1)
    generate_body(world, x = x1 + r, mass=m2, vy = v2, radius=radius2)

    # Add an agent in a circular orbit around the second body
    va = math.sqrt(G*m2/ra)
    generate_moveable_agent(world, x = x1+r+ra, vy = v2+va, mass=agentmass)