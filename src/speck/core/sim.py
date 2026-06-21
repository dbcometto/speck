"""Simulation process"""
import time
import math
import multiprocessing

from speck.core import World

from speck.systems.dynamics import (
    ResetAccelerationSystem, ResetAngularAccelerationSystem,
    GravitySystem, MovementSystem, AttitudeSystem
)
from speck.systems.assemblies import AssemblySystem

from speck.scenarios.base_scenarios import generate_scene_smallbody, generate_scene_2smallbody
from speck.scenarios.agent_scenarios import (
    generate_scene_emptythruster, generate_scene_emptythrusterrcs,
    generate_scene_ansible_test, generate_scene_ansible_test2,
    generate_scene_navigator, generate_scene_thread_test,
    generate_scene_identity_test, generate_scene_follower_test,
    generate_scene_mpc_navigator,
)

from speck.ssh import start_ssh_server

from speck.components.dynamics import Position, Velocity, Attitude
from speck.components.rendering import RenderData
from speck.components.functional import Identity
from speck.components.assemblies import Assembly

from speck.config import DT, TIMEWARP


def build_snapshot(world: World) -> dict:
    """Build a renderable snapshot of world state"""
    positions   = world.get_component(Position)
    velocities  = world.get_component(Velocity)
    attitudes   = world.get_component(Attitude)
    renderdatas = world.get_component(RenderData)
    identities  = world.get_component(Identity)
    assemblies  = world.get_component(Assembly)

    entities = {}
    for eid in positions.keys() & renderdatas.keys():
        pos   = positions[eid]
        vel   = velocities.get(eid)
        att   = attitudes.get(eid)
        data  = renderdatas[eid]
        ident = identities.get(eid)

        heading = 0.0
        if att:
            heading = math.atan2(
                2*(att.w*att.z + att.x*att.y),
                1 - 2*(att.y**2 + att.z**2)
            )

        entities[eid] = {
            "x":              pos.x,
            "y":              pos.y,
            "vx":             vel.x if vel else 0.0,
            "vy":             vel.y if vel else 0.0,
            "heading":        heading,
            "render_type":    int(data.render_type),
            "color":          data.color,
            "radius":         data.radius,
            "name":           ident.name if ident else "",
            "classification": ident.classification if ident else "",
            "has_assembly":   eid in assemblies,
        }

    return {
        "entities":       entities,
        "time":           world.time,
        "timewarp":       world.timewarp,
        "last_sub_dt":    world.last_sub_dt,
        "last_sub_steps": world.last_sub_steps,
    }


def handle_request(conn, world: World) -> None:
    """Handle an inspector/assembly request from the render process"""
    if not conn.poll():
        return
    try:
        msg = conn.recv()
    except Exception:
        return

    if msg[0] == "entity":
        eid = msg[1]
        result = {}
        for comp_type, store in world.components.items():
            if eid in store:
                comp = store[eid]
                fields = {}
                for k, v in comp.__dict__.items():
                    try:
                        import pickle
                        pickle.dumps(v)
                        fields[k] = v
                    except Exception:
                        fields[k] = f"<unpicklable: {type(v).__name__}>"
                result[comp_type.__name__] = fields
        conn.send(("entity", eid, result))

    elif msg[0] == "assembly":
        eid = msg[1]
        from speck.components.assemblies import Assembly, PartIdentity, FlowgraphLayout
        assemblies = world.get_component(Assembly)
        identities = world.get_component(PartIdentity)
        layouts    = world.get_component(FlowgraphLayout)
        if eid not in assemblies:
            conn.send(("assembly", eid, None))
            return
        assembly = assemblies[eid]
        layout   = layouts.get(eid)
        parts = {}
        for part_eid in assembly.parts:
            pi = identities.get(part_eid)
            if pi:
                parts[part_eid] = {
                    "name":  pi.name,
                    "ports": pi.ports,
                }
        conn.send(("assembly", eid, {
            "parts":            parts,
            "edges":            assembly.edges,
            "layout_positions": layout.positions if layout else {},
            "layout_flipped":   layout.flipped   if layout else {},
        }))


def run_sim(snapshot_queue, command_queue, request_conn):
    """Simulation process entry point"""
    world = World(timewarp=TIMEWARP, debug_prints=False)

    world.add_system(ResetAccelerationSystem())
    world.add_system(ResetAngularAccelerationSystem())
    world.add_system(GravitySystem())
    world.add_system(AssemblySystem())
    world.add_system(MovementSystem())
    world.add_system(AttitudeSystem())

    # Populate the world — uncomment one
    # generate_scene_smallbody(world)
    # generate_scene_2smallbody(world)
    # generate_scene_emptythruster(world)
    # generate_scene_emptythrusterrcs(world)
    # generate_scene_ansible_test(world)
    # generate_scene_ansible_test2(world)
    # generate_scene_navigator(world)
    # generate_scene_thread_test(world)
    # generate_scene_mpc_navigator(world)
    # generate_scene_identity_test(world)
    generate_scene_follower_test(world)

    start_ssh_server(world, command_queue)
    last_tick_time = time.perf_counter()

    while True:
        t0 = time.perf_counter()

        # Process commands
        while not command_queue.empty():
            try:
                cmd = command_queue.get_nowait()
                if cmd[0] == "timewarp":
                    world.timewarp = cmd[1]
                elif cmd[0] == "msg_write":
                    world.message_network.write(cmd[1], cmd[2])
            except Exception:
                pass

        # Step simulation
        world.update(DT)

        # Handle inspector/assembly requests
        handle_request(request_conn, world)

        # Compute UPS
        now = time.perf_counter()
        ups = 1.0 / (now - last_tick_time) if (now - last_tick_time) > 0 else 0.0
        last_tick_time = now

        # Publish snapshot
        snap = build_snapshot(world)
        snap["ups"] = ups
        snapshot_queue.put(snap)

        # Sleep to maintain target UPS
        elapsed = time.perf_counter() - t0
        sleep_time = DT - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)