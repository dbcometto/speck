# This is the world
import time

from entities import Rock, Agent
from components import Position, Velocity, Acceleration, Radius, Forces
from systems import FunctionalityGroup, DynamicsGroup, RenderGroup 



class World:
    def __init__(self,entitylist=None,hz=20,timewarp=1,worldsize=200):
        
        self.hz = hz
        self.dt = 1/hz
        self.timewarp = timewarp
        self.worldsize = worldsize
        self.past_time = 0
        
        self.entities = entitylist if entitylist else {}
        self.entities_by_id = {}

        self.systems = [
        FunctionalityGroup(),
        DynamicsGroup(dt=self.dt,timewarp=self.timewarp),
        RenderGroup(size=self.worldsize),
        ]


    def spin(self,debugging=False):
        try:
            while True:
                current_time = time.time()

                if (current_time-self.past_time > self.dt):
                    self.past_time = current_time

                    self.update()
                    
                    if debugging:
                        self.debugPrints()

        except KeyboardInterrupt:
            pass


    def update(self):
        self.entities_by_id = {e.id:e for e in self.entities}

        for system in self.systems:
            system.update(self.entities,self.entities_by_id)


    def debugPrints(self):
        for e in self.entities:
            print(f"{type(e)} {e.id}: {e.get(Forces).components}")