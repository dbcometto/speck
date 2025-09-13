# This is the world
import time
import json
import random
import math

from .entities import Entity
from .components import Position, Velocity, Acceleration, Radius, Forces, Thruster
from .components import Behavior_Orbiter
from .systems import BehaviorGroup, FunctionalityGroup, DynamicsGroup
from .factories import create_rock, create_agent
from .render import RenderGroup


class World:
    def __init__(self,worldpath="worlds/world.json",entitylist=None,hz=30,render_hz=2,timewarp=1,worldsize=200):
        
        self.worldpath = worldpath
        self.hz = hz
        self.render_hz = render_hz
        self.dt = 1/hz
        self.render_period = 1/render_hz
        self.timewarp = timewarp
        self.worldsize = worldsize
        self.past_time = 0
        self.past_render_time = 0
        
        self.entities = entitylist if entitylist else []
        self.entities_by_id = {}

        self.systems = [
            BehaviorGroup(),
            FunctionalityGroup(),
            DynamicsGroup(dt=self.dt,timewarp=self.timewarp),
        ]
        self.renderer = RenderGroup(size=self.worldsize)

        self.nextid = 0


    def spin(self,debugging=False):
        try:
            while True:
                current_time = time.time()

                if (current_time-self.past_time > self.dt):
                    t0 = time.perf_counter()

                    if (current_time-self.past_render_time > self.render_period):
                        self.past_render_time = current_time
                        doRender = True
                    else:
                        doRender = False

                    self.past_time = current_time
                    self.update(doRender)

                    t1 = time.perf_counter()
                    print(f"{doRender} {t1-t0:8.4f}")


        except KeyboardInterrupt:
            print("KeyboardInterrupt caught, closing world")
        except Exception as e:
            import traceback
            print("Exception occurred:")
            traceback.print_exc()  # full exception info


    def update(self,doRender):
        self.entities_by_id = {e.id:e for e in self.entities}

        for system in self.systems:
            # t0 = time.perf_counter()
            system.update(self.entities,self.entities_by_id)
            # t1 = time.perf_counter()
            # print(f"{type(system)}: {t1-t0:8.4f}")

        if doRender:
            # t0 = time.perf_counter()
            self.renderer.update(self.entities,self.entities_by_id)
            # t1 = time.perf_counter()
            # print(f"{type(self.renderer)}: {t1-t0:8.4f}")
            

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


    def add_entity(self,entity):
        self.entities.append(entity)



    def generate(self,boundary=1000,max_rocks=100,max_iterations=100):
        for i in range(max_rocks):
            min_radius = 1
            max_radius = 15
            radius = max(min_radius,random.random()*max_radius)

            min_mass = 1
            max_mass = 1e6
            mass = max(min_mass,random.random()*max_mass)

            posEstablished = False
            iterations = 0
            while not posEstablished and (iterations < max_iterations):
                posx = random.uniform(-boundary,boundary)
                posy = random.uniform(-boundary,boundary)

                for e in self.entities:
                    ePos = e.get(Position)
                    eRadius = e.get(Radius)

                    if ePos and eRadius:
                        d = math.hypot(posx-ePos.x,posy-ePos.y)

                        if d > eRadius.radius + radius:
                            posEstablished
                
                iterations += 1

            max_vel = 10
            velx = random.uniform(-max_vel,max_vel)
            vely = random.uniform(-max_vel,max_vel)

            self.add_entity(create_rock(entity_id=self.nextid,position=(posx,posy),velocity=(velx,vely),radius=radius,mass=mass))



        
