"""Define scenarios using the agent SDK"""
from speck.core import World

import random
import math
import time
import queue
import threading

from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.optimize import minimize

from speck.sdk.agent import Agent
from speck.sdk.parts import (
    Thruster, Tank, Computer, AttitudeController, 
    Ansible, PositionSensor, VelocitySensor, HeadingSensor, AngularVelocitySensor
)




# ================ Simple Tests ================ #

class ThrusterTestAgent(Agent):
    def define(self):
        # Add parts
        tank     = self.add(Tank("fuel", capacity=1000.0, fill=1000.0))
        thruster = self.add(Thruster(max_thrust=1.0))
        cpu      = self.add(Computer(outputs=["throttle_out"]))

        # Connect parts
        self.connect(tank.fuel_out,       thruster.fuel_in)
        self.connect(cpu.throttle_out,    thruster.throttle_in)

        # Add scripts
        cpu.run(self.control, period=1.0)

    def control(self, ports, dt):
        ports.throttle_out = random.uniform(0, 1)

def generate_scene_emptythruster(world: World):
    world.spawn(ThrusterTestAgent, mass=1)



class ThrusterRCSTestAgent(Agent):
    def define(self):
        # Add parts
        tank     = self.add(Tank("fuel", capacity=1000.0, fill=1000.0))
        thruster = self.add(Thruster(max_thrust=1.0))
        rcs      = self.add(AttitudeController(max_torque=1.0))
        cpu      = self.add(Computer(outputs=["throttle_out", "attitude_out"]))

        # Connect parts
        self.connect(tank.fuel_out,       thruster.fuel_in)
        self.connect(cpu.throttle_out,    thruster.throttle_in)
        self.connect(cpu.attitude_out,    rcs.control_in)

        # Add scripts
        cpu.run(self.control, period=1.0)

    def control(self, ports, dt):
        ports.throttle_out = random.uniform(0, 1)
        ports.attitude_out = random.uniform(-1, 1)

def generate_scene_emptythrusterrcs(world: World):
    world.spawn(ThrusterRCSTestAgent, mass=1)



# ================ Messaging Tests ================ #

class AgentA(Agent):
    def define(self):
        tank     = self.add(Tank("fuel", capacity=1000.0, fill=1000.0))
        thruster = self.add(Thruster(max_thrust=1.0))
        rcs      = self.add(AttitudeController(max_torque=1.0))
        ansible  = self.add(Ansible(transmit={"message_out": "a_to_b"}))
        cpu      = self.add(Computer(outputs=["throttle_out", "attitude_out", "message_out"]))

        self.connect(tank.fuel_out,       thruster.fuel_in)
        self.connect(cpu.throttle_out,    thruster.throttle_in)
        self.connect(cpu.attitude_out,    rcs.control_in)
        self.connect(cpu.message_out,     ansible.message_out)

        cpu.run(self.control, period=1.0)

    def control(self, ports, dt):
        ports.throttle_out  = random.uniform(0, 1)
        ports.attitude_out  = random.uniform(-1, 1)
        ports.message_out   = f"hello from A: {random.randint(0, 1000)}"


class AgentB(Agent):
    def define(self):
        tank     = self.add(Tank("fuel", capacity=1000.0, fill=1000.0))
        thruster = self.add(Thruster(max_thrust=1.0))
        rcs      = self.add(AttitudeController(max_torque=1.0))
        ansible  = self.add(Ansible(receive={"a_to_b": "message_in"}))
        cpu      = self.add(Computer(
            inputs=["message_in"],
            outputs=["throttle_out", "attitude_out"]
        ))

        self.connect(tank.fuel_out,       thruster.fuel_in)
        self.connect(cpu.throttle_out,    thruster.throttle_in)
        self.connect(cpu.attitude_out,    rcs.control_in)
        self.connect(ansible.message_in,  cpu.message_in)

        cpu.run(self.control, period=1.0)

    def control(self, ports, dt):
        ports.throttle_out = random.uniform(0, 1)
        ports.attitude_out = random.uniform(-1, 1)
        # if ports.message_in:
        #     print(f"Agent B received: {ports.message_in}")


def generate_scene_ansible_test(world: World):
    world.spawn(AgentA, x=0,  y=0, mass=1, name="Agent A")
    world.spawn(AgentB, x=10, y=0, mass=1, name="Agent B")


def generate_scene_ansible_test2(world: World):
    world.spawn(AgentB, x=10, y=0, mass=1, name="Agent B")





# ================ PID Navigator ================ #

class Navigator(Agent):
    def define(self):
        tank     = self.add(Tank("fuel", capacity=1000.0, fill=1000.0))
        thruster = self.add(Thruster(max_thrust=1.0))
        rcs      = self.add(AttitudeController(max_torque=1.0))
        pos      = self.add(PositionSensor())
        hdg      = self.add(HeadingSensor())
        vel      = self.add(VelocitySensor())
        ansible  = self.add(Ansible(receive={"target": "target_in"}))
        cpu      = self.add(Computer(
            inputs=["x", "y", "heading", "vx", "vy", "target_in"],
            outputs=["throttle_out", "attitude_out"]
        ))

        self.connect(tank.fuel_out,     thruster.fuel_in)
        self.connect(cpu.throttle_out,  thruster.throttle_in)
        self.connect(cpu.attitude_out,  rcs.control_in)
        self.connect(pos.x,             cpu.x)
        self.connect(pos.y,             cpu.y)
        self.connect(hdg.heading,       cpu.heading)
        self.connect(vel.vx,            cpu.vx)
        self.connect(vel.vy,            cpu.vy)
        self.connect(ansible.target_in, cpu.target_in)

        state = {
            "target": None,
            "h_integral": 0.0,
            "h_prev_error": 0.0,
            "t_integral": 0.0,
            "t_prev_error": 0.0,
        }

        H_KP, H_KI, H_KD = 0.1, 0.0, 0.5
        T_KP, T_KI, T_KD = 0.1, 0.0, 0.05

        def control(ports, dt):
            if ports.target_in is not None:
                state["target"] = ports.target_in
                state["h_integral"] = 0.0
                state["t_integral"] = 0.0

            if state["target"] is None or ports.x is None:
                ports.throttle_out = 0.0
                ports.attitude_out = 0.0
                return

            tx, ty = state["target"]
            dx = tx - ports.x
            dy = ty - ports.y
            dist = math.sqrt(dx**2 + dy**2)

            # heading PID
            desired_heading = math.atan2(dy, dx)
            h_error = desired_heading - ports.heading
            while h_error >  math.pi: h_error -= 2*math.pi
            while h_error < -math.pi: h_error += 2*math.pi

            state["h_integral"] += h_error * dt
            h_derivative = (h_error - state["h_prev_error"]) / dt if dt > 0 else 0.0
            state["h_prev_error"] = h_error

            attitude_cmd = H_KP*h_error + H_KI*state["h_integral"] + H_KD*h_derivative
            attitude_cmd = max(-1.0, min(1.0, attitude_cmd))

            # throttle PID — only when aligned
            if abs(h_error) < 0.3:
                t_error = dist
                state["t_integral"] += t_error * dt
                t_derivative = (t_error - state["t_prev_error"]) / dt if dt > 0 else 0.0
                state["t_prev_error"] = t_error
                throttle_cmd = T_KP*t_error + T_KI*state["t_integral"] + T_KD*t_derivative
                throttle_cmd = max(0.0, min(1.0, throttle_cmd))
            else:
                state["t_prev_error"] = 0.0
                state["t_integral"]   = 0.0
                throttle_cmd = 0.0

            ports.attitude_out = attitude_cmd
            ports.throttle_out = throttle_cmd

        cpu.run(control, period=0.1)


def generate_scene_navigator(world):
    world.spawn(Navigator, x=0, y=0, mass=1, name="Navigator")


# ================ Multithreading Test ================ #

class ThreadTest(Agent):
    def define(self):
        tank     = self.add(Tank("fuel", capacity=1000.0, fill=1000.0))
        thruster = self.add(Thruster(max_thrust=1.0))
        rcs      = self.add(AttitudeController(max_torque=1.0))
        cpu      = self.add(Computer(outputs=["throttle_out", "attitude_out"]))

        self.connect(tank.fuel_out,    thruster.fuel_in)
        self.connect(cpu.throttle_out, thruster.throttle_in)
        self.connect(cpu.attitude_out, rcs.control_in)

        def control(ports, dt):
            time.sleep(1.0)
            ports.throttle_out = 0.5
            ports.attitude_out = 0.0

        cpu.run(control, period=0.1, threaded=True)


def generate_scene_thread_test(world):
    world.spawn(ThreadTest, x=0, y=0, mass=1, name="ThreadTest")










# ================ MPC Navigator ================ #

def dynamics(state, control, dt, max_thrust, max_torque):
    x, y, vx, vy, theta, omega = state
    throttle, torque = control

    ax    = math.cos(theta) * throttle * max_thrust
    ay    = math.sin(theta) * throttle * max_thrust
    alpha = torque * max_torque

    return [
        x     + vx    * dt,
        y     + vy    * dt,
        vx    + ax    * dt,
        vy    + ay    * dt,
        theta + omega * dt,
        omega + alpha * dt,
    ]

def make_warm_start(state, target, horizon, dt, max_thrust, max_torque):
    x, y, vx, vy, theta, omega = state
    tx, ty = target
    
    speed = math.sqrt(vx**2 + vy**2)
    dist  = math.sqrt((tx-x)**2 + (ty-y)**2)
    
    brake_time  = speed / max_thrust if speed > 0.1 else 0.0
    brake_steps = min(int(brake_time / dt), horizon)
    travel_time  = math.sqrt(2 * dist / max_thrust) if dist > 0.1 else 0.0
    travel_steps = min(int(travel_time / dt), horizon - brake_steps)

    u0 = np.zeros((horizon, 2))

    if speed > 0.1:
        retrograde = math.atan2(-vy, -vx)
        heading_error = retrograde - theta
        while heading_error >  math.pi: heading_error -= 2*math.pi
        while heading_error < -math.pi: heading_error += 2*math.pi
        for i in range(brake_steps):
            u0[i] = [1.0 if abs(heading_error) < 0.3 else 0.0,
                     max(-1.0, min(1.0, heading_error * 2.0))]

    for i in range(brake_steps, brake_steps + travel_steps):
        u0[i] = [1.0, 0.0]

    return u0


def solve_mpc(state, target, horizon, dt, max_thrust, max_torque, u_init=None):
    W_POS, W_VEL, W_INPUT = 10.0, 1.0, 0.1

    def cost(u_flat):
        u = u_flat.reshape(horizon, 2)
        s = list(state)
        c = 0.0
        for i in range(horizon):
            s  = dynamics(s, u[i], dt, max_thrust, max_torque)
            dx = s[0] - target[0]
            dy = s[1] - target[1]
            c += W_POS * (dx**2 + dy**2)
            c += W_VEL * (s[2]**2 + s[3]**2)
            c += W_INPUT * (u[i][0]**2 + u[i][1]**2)
        c += 30.0 * (s[2]**2 + s[3]**2)
        c += 30.0 * s[5]**2
        return c

    bounds = []
    for _ in range(horizon):
        bounds.append((0, 1))
        bounds.append((-1, 1))

    if u_init is not None:
        u0 = np.vstack([u_init[1:], u_init[-1:]]).flatten()
    else:
        u0 = make_warm_start(state, target, horizon, dt, max_thrust, max_torque).flatten()

    result = minimize(cost, u0, method='SLSQP', bounds=bounds,
                      options={'maxiter': 100, 'ftol': 1e-4})

    if result.success:
        return result.x.reshape(horizon, 2), True
    else:
        return u0.reshape(horizon, 2), False


class MPCNavigator(Agent):
    def define(self):
        max_thrust = 1.0
        max_torque = 1.0

        tank     = self.add(Tank("fuel", capacity=1000.0, fill=1000.0))
        thruster = self.add(Thruster(max_thrust=max_thrust))
        rcs      = self.add(AttitudeController(max_torque=max_torque))
        pos      = self.add(PositionSensor())
        hdg      = self.add(HeadingSensor())
        vel      = self.add(VelocitySensor())
        omg      = self.add(AngularVelocitySensor())
        ansible  = self.add(Ansible(receive={"target": "target_in"}))
        cpu      = self.add(Computer(
            inputs=["x", "y", "vx", "vy", "heading", "omega", "target_in"],
            outputs=["throttle_out", "attitude_out"]
        ))

        self.connect(tank.fuel_out,     thruster.fuel_in)
        self.connect(cpu.throttle_out,  thruster.throttle_in)
        self.connect(cpu.attitude_out,  rcs.control_in)
        self.connect(pos.x,             cpu.x)
        self.connect(pos.y,             cpu.y)
        self.connect(hdg.heading,       cpu.heading)
        self.connect(vel.vx,            cpu.vx)
        self.connect(vel.vy,            cpu.vy)
        self.connect(omg.omega,         cpu.omega)
        self.connect(ansible.target_in, cpu.target_in)

        executor = ProcessPoolExecutor(max_workers=1)
        state = {
            "target":   None,
            "last_cmd": (0.0, 0.0),
            "u_prev":   None,
            "future":   None,
        }

        MPC_DT      = 0.1
        MPC_HORIZON = 30

        def control(ports, dt):
            if ports.target_in is not None:
                state["target"] = ports.target_in
                state["u_prev"] = None

            if state["target"] is None or ports.x is None:
                ports.throttle_out = 0.0
                ports.attitude_out = 0.0
                return

            s = [
                ports.x, ports.y,
                ports.vx or 0.0, ports.vy or 0.0,
                ports.heading, ports.omega or 0.0
            ]

            if state["future"] is not None and state["future"].done():
                try:
                    u_opt, success = state["future"].result()
                    if success:
                        state["u_prev"] = u_opt
                        state["last_cmd"] = (float(u_opt[0][0]), float(u_opt[0][1]))
                except Exception as e:
                    print(f"MPC process error: {e}")
                state["future"] = None

            if state["future"] is None:
                state["future"] = executor.submit(
                    solve_mpc, s, state["target"],
                    MPC_HORIZON, MPC_DT,
                    max_thrust, max_torque,
                    state["u_prev"]
                )

            ports.throttle_out, ports.attitude_out = state["last_cmd"]

        cpu.run(control, period=MPC_DT)


def generate_scene_mpc_navigator(world):
    world.spawn(MPCNavigator, x=0, y=0, mass=1, name="MPC Navigator")