"""Systems for processing assemblies and parts"""
from __future__ import annotations
from typing import Any
from collections import defaultdict

from ..core import World
from ..components.assemblies import (
    Assembly, PartIdentity, ScriptBehavior,
    ThrusterBehavior, AttitudeBehavior, ResourceBehavior,
    PORT_TYPE, PORT_DIRECTION
)
from ..components.dynamics import Acceleration, AngularAcceleration, Attitude
from .system import System


_PortKey = tuple[int, str]
_Network = list[_PortKey]


class AssemblySystem(System):
    """Processes all assemblies each tick"""

    def update(self, world: World, dt: float) -> None:
        """Processes all assemblies each tick"""
        assemblies = world.get_component(Assembly)
        identities = world.get_component(PartIdentity)
        scripts    = world.get_component(ScriptBehavior)
        thrusters  = world.get_component(ThrusterBehavior)
        attitudes  = world.get_component(AttitudeBehavior)
        resources  = world.get_component(ResourceBehavior)
        accels     = world.get_component(Acceleration)
        attitude_components = world.get_component(Attitude)
        ang_accels = world.get_component(AngularAcceleration)

        for assembly_eid, assembly in assemblies.items():
            self._run_scripts(assembly_eid, assembly, identities, scripts, world, dt)
            self._propagate_data(assembly, identities)
            self._update_rates(assembly, identities, thrusters, resources)
            self._settle_resources(assembly, identities, resources, dt)
            self._apply_effects(assembly_eid, assembly, identities, thrusters,
                                attitudes, resources, accels, ang_accels, attitude_components, dt)



    # Port Helpers

    def _get_port(self, identity: PartIdentity,
                  port_name: str) -> tuple[str, PORT_TYPE, PORT_DIRECTION] | None:
        return next((p for p in identity.ports if p[0] == port_name), None)

    def _read_port(self, identity: PartIdentity,
                   port_name: str, default: Any = None) -> Any:
        return identity.port_values.get(port_name, default)



    # Network Helpers

    def _build_networks(self, assembly: Assembly,
                        identities: dict[int, PartIdentity],
                        port_type: PORT_TYPE) -> list[_Network]:
        adj: dict[_PortKey, list[_PortKey]] = defaultdict(list)

        for from_eid, from_port, to_eid, to_port in assembly.edges:
            if from_eid not in identities or to_eid not in identities:
                continue
            fp = self._get_port(identities[from_eid], from_port)
            tp = self._get_port(identities[to_eid],   to_port)
            if fp is None or tp is None or fp[1] != port_type or tp[1] != port_type:
                continue
            adj[(from_eid, from_port)].append((to_eid, to_port))
            adj[(to_eid,   to_port)].append((from_eid, from_port))

        visited:  set[_PortKey]  = set()
        networks: list[_Network] = []

        for node in adj:
            if node in visited:
                continue
            network: _Network = []
            queue = [node]
            while queue:
                curr = queue.pop()
                if curr in visited:
                    continue
                visited.add(curr)
                network.append(curr)
                queue.extend(adj[curr])
            networks.append(network)

        return networks


    def _settle_network(self, network: _Network,
                        identities: dict[int, PartIdentity],
                        resources:  dict[int, ResourceBehavior],
                        dt: float) -> None:
        suppliers: list[tuple[int, str, float]] = []
        consumers: list[tuple[int, str, float]] = []

        for part_eid, port_name in network:
            if part_eid not in resources or part_eid not in identities:
                continue
            rb          = resources[part_eid]
            storage_key = rb.port_mapping.get(port_name)
            if storage_key is None:
                continue
            port = self._get_port(identities[part_eid], port_name)
            if port is None:
                continue

            rate_entry = rb.rates.get(storage_key)
            rate       = (rate_entry[1] or 0.0) if rate_entry else 0.0
            stored     = rb.stored.get(storage_key) or 0.0
            cap_entry  = rb.capacities.get(storage_key)
            capacity   = cap_entry[1] if cap_entry else None

            if port[2] == PORT_DIRECTION.OUT:
                available = min(stored, rate * dt)
                if available > 0:
                    suppliers.append((part_eid, storage_key, available))
            else:
                space  = (capacity - stored) if capacity is not None else rate * dt
                wanted = min(space, rate * dt)
                if wanted > 0:
                    consumers.append((part_eid, storage_key, wanted))

        total_supply = sum(a for _, _, a in suppliers)
        total_demand = sum(w for _, _, w in consumers)

        if total_supply == 0 or total_demand == 0:
            return

        flow = min(total_supply, total_demand)

        for part_eid, storage_key, available in suppliers:
            resources[part_eid].stored[storage_key] -= flow * (available / total_supply)

        for part_eid, storage_key, wanted in consumers:
            rb = resources[part_eid]
            rb.stored[storage_key] = (rb.stored.get(storage_key) or 0.0) + flow * (wanted / total_demand)



    # Processing Steps

    def _run_scripts(self, assembly_eid: int,
                     assembly:     Assembly,
                     identities:   dict[int, PartIdentity],
                     scripts:      dict[int, ScriptBehavior],
                     world:        World,
                     dt:           float) -> None:
        for part_eid in assembly.parts:
            if part_eid not in scripts or part_eid not in identities:
                continue
            sb      = scripts[part_eid]
            outputs: dict[str, Any] | None = sb.script.update(assembly_eid, world, dt)
            if not outputs:
                continue
            pi = identities[part_eid]
            for script_port, value in outputs.items():
                real_port = sb.port_mapping.get(script_port, script_port)
                if real_port in pi.port_values:
                    pi.port_values[real_port] = value

    def _propagate_data(self, assembly:   Assembly,
                        identities: dict[int, PartIdentity]) -> None:
        for from_eid, from_port, to_eid, to_port in assembly.edges:
            if from_eid not in identities or to_eid not in identities:
                continue
            fp = self._get_port(identities[from_eid], from_port)
            if fp is None or fp[1] != PORT_TYPE.DATA:
                continue
            value = identities[from_eid].port_values.get(from_port)
            if to_port in identities[to_eid].port_values:
                identities[to_eid].port_values[to_port] = value

    def _update_rates(self, assembly:   Assembly,
                      identities: dict[int, PartIdentity],
                      thrusters:  dict[int, ThrusterBehavior],
                      resources:  dict[int, ResourceBehavior]) -> None:
        for part_eid in assembly.parts:
            if part_eid not in identities:
                continue
            pi = identities[part_eid]

            if part_eid in thrusters and part_eid in resources:
                tb       = thrusters[part_eid]
                throttle = self._read_port(pi, tb.control_port, 0.0) or 0.0
                rb       = resources[part_eid]
                if tb.fuel_storage_key in rb.rates:
                    port_type = rb.rates[tb.fuel_storage_key][0]
                    rb.rates[tb.fuel_storage_key] = (port_type, throttle * tb.max_thrust)

    def _settle_resources(self, assembly:   Assembly,
                          identities: dict[int, PartIdentity],
                          resources:  dict[int, ResourceBehavior],
                          dt:         float) -> None:
        for port_type in PORT_TYPE:
            if port_type == PORT_TYPE.DATA:
                continue
            for network in self._build_networks(assembly, identities, port_type):
                self._settle_network(network, identities, resources, dt)

    def _apply_effects(self, assembly_eid: int,
                       assembly:     Assembly,
                       identities:   dict[int, PartIdentity],
                       thrusters:    dict[int, ThrusterBehavior],
                       attitudes:    dict[int, AttitudeBehavior],
                       resources:    dict[int, ResourceBehavior],
                       accels:       dict[int, Acceleration],
                       ang_accels:   dict[int, AngularAcceleration],
                       attitude_components: dict[int, Attitude],
                       dt:           float) -> None:
        if assembly_eid not in accels or assembly_eid not in ang_accels:
            return
        acc     = accels[assembly_eid]
        ang_acc = ang_accels[assembly_eid]

        for part_eid in assembly.parts:
            if part_eid not in identities:
                continue
            pi = identities[part_eid]

            # Thruster behavior
            if part_eid in thrusters and part_eid in resources:
                tb       = thrusters[part_eid]
                throttle = self._read_port(pi, tb.control_port, 0.0) or 0.0
                rb       = resources[part_eid]
                stored   = rb.stored.get(tb.fuel_storage_key) or 0.0

                if throttle and stored > 0:
                    consumed = min(stored, throttle * tb.max_thrust * dt)
                    rb.stored[tb.fuel_storage_key] -= consumed

                    attitude = attitude_components.get(assembly_eid)
                    if attitude:
                        # parse body-frame axis from tb.axis e.g. "+x" -> (1,0,0)
                        axis_map = {
                            "+x": (1,0,0), "-x": (-1,0,0),
                            "+y": (0,1,0), "-y": (0,-1,0),
                            "+z": (0,0,1), "-z": (0,0,-1),
                        }
                        bx, by, bz = axis_map.get(tb.axis, (1,0,0))
                        wx, wy, wz = self._rotate_vector_by_quaternion(
                            bx, by, bz,
                            attitude.w, attitude.x, attitude.y, attitude.z
                        )
                        force = throttle * tb.max_thrust
                        acc.x += force * wx
                        acc.y += force * wy
                        acc.z += force * wz


            # Attitude Behavior
            if part_eid in attitudes:
                ab      = attitudes[part_eid]
                control = self._read_port(pi, ab.control_port, 0.0) or 0.0
                if control:
                    ang_acc.z += control * ab.max_torque  # TODO: apply axis








    # Other helpers

    def _rotate_vector_by_quaternion(self, vx, vy, vz, qw, qx, qy, qz) -> tuple[float, float, float]:
        # rotate vector (vx,vy,vz) by quaternion (qw,qx,qy,qz)
        # using v' = q v q*
        tx = 2 * (qy * vz - qz * vy)
        ty = 2 * (qz * vx - qx * vz)
        tz = 2 * (qx * vy - qy * vx)
        return (
            vx + qw * tx + qy * tz - qz * ty,
            vy + qw * ty + qz * tx - qx * tz,
            vz + qw * tz + qx * ty - qy * tx,
    )