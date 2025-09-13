# This holds any utilies we might need
import math
from typing import Tuple

from .entities import Entity

from .components import Position, Velocity, Acceleration, Forces
from .components import Radius, Mass
from .components import Thruster


Distance = float
DistanceVector = Tuple[float,float]
DistanceUnitVector = Tuple[float,float]

def calc_distance(e1:Entity, e2:Entity) -> Tuple[Distance,DistanceVector,DistanceUnitVector]:
    """
    Calculates the distance from Entity e1 to Entity e2.

    ### Returns 

    d, (dx,dy), (ux,uy)
    - d      : scalar distance
    - (dx,dy): distance vector
    - (ux,uy): distance unit vector
    """
    pos1 = e1.get(Position)
    pos2 = e2.get(Position)

    dx = pos2.x - pos1.x
    dy = pos2.y - pos1.y

    d = math.sqrt(dx**2+dy**2)

    ux = dx/d
    uy = dy/d

    return d, (dx,dy), (ux,uy)