import math
from entities import Entity
from components import Mass, Position, Forces
from factories import create_rock, create_agent


class Body:
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass
        self.fx = 0.0
        self.fy = 0.0

class QuadNode:
    def __init__(self, x_min, x_max, y_min, y_max):
        self.bounds = (x_min, x_max, y_min, y_max)
        self.mass = 0.0
        self.com_x = 0.0
        self.com_y = 0.0
        self.entity = None
        self.children = []

    def insert(self, entity):
        # If empty leaf, store body
        mass = entity.get(Mass)
        pos = entity.get(Position)

        if not mass and pos:
            return
        
        mass = mass.mass

        if self.entity is None and not self.children:
            self.entity = entity
            self.mass = mass
            self.com_x = pos.x
            self.com_y = pos.y
            return

        # If this node already has a body, subdivide
        if self.children == []:
            self.subdivide()
            self._push_down(self.entity)
            self.entity = None  # clear leaf

        # Insert new body into correct quadrant
        self._push_down(entity)

        # Update mass + COM
        self.com_x = (self.com_x * self.mass + pos.x * mass) / (self.mass + mass)
        self.com_y = (self.com_y * self.mass + pos.y * mass) / (self.mass + mass)
        self.mass += mass

    def _push_down(self, entity):
        pos = entity.get(Position)

        if not pos:
            return

        for child in self.children:
            x_min, x_max, y_min, y_max = child.bounds
            if x_min <= pos.x < x_max and y_min <= pos.y < y_max:
                child.insert(entity)
                return

    def subdivide(self):
        x_min, x_max, y_min, y_max = self.bounds
        x_mid = (x_min + x_max) / 2
        y_mid = (y_min + y_max) / 2
        self.children = [
            QuadNode(x_min, x_mid, y_min, y_mid),  # bottom-left
            QuadNode(x_mid, x_max, y_min, y_mid),  # bottom-right
            QuadNode(x_min, x_mid, y_mid, y_max),  # top-left
            QuadNode(x_mid, x_max, y_mid, y_max),  # top-right
        ]




def compute_force(entity, node, G=1.0, theta=0.5, eps=0.01):
    mass = entity.get(Mass)
    pos = entity.get(Position)
    forces = entity.get(Forces)

    if not mass and pos:
        return
    
    mass = mass.mass

    if node.mass == 0 or (node.entity is entity and not node.children):
        return

    dx = node.com_x - pos.x
    dy = node.com_y - pos.y
    dist = math.sqrt(dx*dx + dy*dy) + eps

    if node.children:
        x_min, x_max, y_min, y_max = node.bounds
        s = max(x_max - x_min, y_max - y_min)
        # Barnes-Hut approximation
        if s / dist < theta:
            F = G * mass * node.mass / (dist**2)
            fx, fy = forces.components.get("Gravity", (0,0))
            fx += F * dx / dist
            fy += F * dy / dist
            forces.components["Gravity"] = (fx, fy)
            return
        else:
            for child in node.children:
                compute_force(entity, child, G, theta, eps)
            return
    else:
        # Leaf node (single body)
        if node.entity is not entity:
            F = G * mass * node.mass / (dist**2)
            fx, fy = forces.components.get("Gravity", (0,0))
            fx += F * dx / dist
            fy += F * dy / dist
            forces.components["Gravity"] = (fx, fy)

# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    # Create some bodies

    entities = [
        create_rock(1,(0,0),mass=10),
        create_rock(2,(1,1),mass=10),
        create_rock(3,(-2,2),mass=10),
        create_rock(4,(5,10),mass=10)
    ]

    x_min = min(e.get(Position).x if e.has(Position) else None for e in entities)
    x_max = max(e.get(Position).x if e.has(Position) else None for e in entities)
    y_min = min(e.get(Position).y if e.has(Position) else None for e in entities)
    y_max = max(e.get(Position).y if e.has(Position) else None for e in entities)
    root = QuadNode(x_min, x_max, y_min, y_max)
    for e in entities:
        root.insert(e)

    # Compute forces
    for e in entities:
        compute_force(e, root)
        print(f"{type(e)} {e.id}: force=({e.get(Forces).components})")
