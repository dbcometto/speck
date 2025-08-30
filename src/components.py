# Component definitions

# Dynamics

class Position:
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y

class Velocity:
    def __init__(self,vx=0,vy=0):
        self.x = vx
        self.y = vy

class Acceleration:
    def __init__(self,ax=0,ay=0):
        self.x = ax
        self.y = ay

class Forces:
    def __init__(self,components={}):
        self.components = components       # dictionary of form {"force_name":(fx,fy)}
        self.total_x = 0
        self.total_y = 0



# Attributes

class Radius:
    def __init__(self,radius):
        self.radius = radius

class Mass:
    def __init__(self,mass):
        self.mass = mass