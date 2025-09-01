# This is the world
import time
import json

from entities import Entity, Rock, Agent
from components import Position, Velocity, Acceleration, Radius, Forces, Thruster
from components import Behavior_Orbiter
from systems import BehaviorGroup, FunctionalityGroup, DynamicsGroup, RenderGroup 



class World:
    def __init__(self,worldpath="worlds/world.json",entitylist=None,hz=60,timewarp=1,worldsize=200):
        
        self.worldpath = worldpath
        self.hz = hz
        self.dt = 1/hz
        self.timewarp = timewarp
        self.worldsize = worldsize
        self.past_time = 0
        
        self.entities = entitylist if entitylist else {}
        self.entities_by_id = {}

        self.systems = [
            BehaviorGroup(),
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

        except KeyboardInterrupt:
            print("KeyboardInterrupt caught, closing world")
        except Exception as e:
            import traceback
            print("Exception occurred:")
            traceback.print_exc()  # full exception info


    def update(self):
        self.entities_by_id = {e.id:e for e in self.entities}

        for system in self.systems:
            system.update(self.entities,self.entities_by_id)


    def save(self):
        entity_list_dicts = [e.to_dict() for e in self.entities]
        with open(self.worldpath, "w") as f:
            json.dump(entity_list_dicts, f, indent=4)

    def load(self):
        """Load a world from a JSON file."""
        try:
            with open(self.worldpath, "r") as f:
                data = json.load(f)

            self.entities = [Entity.from_dict(d) for d in data]
        except:
            print("Failed to load world")



    # def generate(self,bounds=(1000,1000)):

        
