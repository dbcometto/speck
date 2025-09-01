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

class Width:
    def __init__(self,width):
        self.width = width                    # in km



# More things

class Thruster:
    def __init__(self,max_thrust=1):
        self.max_thrust = max_thrust
        self.thrust_x = 0
        self.thrust_y = 0
        self.desired_thrust_x = 0
        self.desired_thrust_y = 0
        self.throttle=0


# AI Attributes

class Behavior_RandomThruster:
    def __init__(self):
        pass


class Behavior_Orbiter:
    def __init__(self,orbit_id,orbit_distance,vel_tolerance = 0.5):
        self.orbit_id = orbit_id
        self.orbit_distance = orbit_distance