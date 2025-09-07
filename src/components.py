# Component definitions

# Dynamics

class Position:
    def __init__(self,x=0,y=0):
        self.x = x                          # in km
        self.y = y                          # in km

class Velocity:
    def __init__(self,x=0,y=0):
        self.x = x                         # in km/s
        self.y = y                         # in km/s

class Acceleration:
    def __init__(self,x=0,y=0):
        self.x = x                         # in km/s^2
        self.y = y                         # in km/s^2

class Forces:
    def __init__(self,components=None,total_x=0,total_y=0):
        self.components = components if components else {}        # dictionary of form {"force_name":(fx,fy)}
        self.total_x = total_x                    # in MN = t km/s^2
        self.total_y = total_y                    # in MN = t km/s^2



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
    def __init__(self,max_thrust=1,thrust_x=0,thrust_y=0,desired_thrust_x=0,desired_thrust_y=0,throttle=0):
        self.max_thrust = max_thrust
        self.thrust_x = thrust_x
        self.thrust_y = thrust_y
        self.desired_thrust_x = desired_thrust_x
        self.desired_thrust_y = desired_thrust_y
        self.throttle = throttle


# AI Attributes

class Behavior_RandomThruster:
    def __init__(self):
        pass


class Behavior_Orbiter:
    def __init__(self,orbit_id,orbit_distance):
        self.orbit_id = orbit_id
        self.orbit_distance = orbit_distance



# Rendering

class Render_Data:
    def __init__(self,shape,color):
        self.shape = shape
        self.color = color






component_types = {
    "Position"                  : Position,
    "Velocity"                  : Velocity,
    "Acceleration"              : Acceleration,
    "Forces"                    : Forces,
    "Radius"                    : Radius,
    "Mass"                      : Mass,
    "Width"                     : Width,
    "Thruster"                  : Thruster,
    "Behavior_RandomThruster"   : Behavior_RandomThruster,
    "Behavior_Orbiter"          : Behavior_Orbiter,
    "Render_Data"               : Render_Data,
}