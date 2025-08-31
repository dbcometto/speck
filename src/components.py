# Component definitions

# Dynamics

class Position:
    def __init__(self,x=0,y=0):
        self.x = x                          # in km
        self.y = y                          # in km

class Velocity:
    def __init__(self,vx=0,vy=0):
        self.x = vx                         # in km/s
        self.y = vy                         # in km/s

class Acceleration:
    def __init__(self,ax=0,ay=0):
        self.x = ax                         # in km/s^2
        self.y = ay                         # in km/s^2

class Forces:
    def __init__(self,components={}):
        self.components = components        # dictionary of form {"force_name":(fx,fy)}
        self.total_x = 0                    # in MN = t km/s^2
        self.total_y = 0                    # in MN = t km/s^2



# Attributes

class Radius:
    def __init__(self,radius):
        self.radius = radius                # in km

class Mass:
    def __init__(self,mass):
        self.mass = mass                    # in t = Mg = 1000 kg



# More things

class Thruster:
    def __init__(self,max_thrust=1):
        self.max_thrust = max_thrust
        self.current_thrust = (0,0)