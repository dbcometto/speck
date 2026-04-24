"""Systems for processing assemblies and parts"""
from ..core import World
from ..components.assemblies import Assembly, PartIdentity, ScriptBehavior
from ..components.assemblies import ThrusterBehavior, RCSBehavior
from ..components.dynamics import Acceleration, AngularAcceleration
from .system import System

class AssemblySystem(System):
    """Processes all assemblies each tick"""

    def update(self, world: World, dt: float) -> None:
        assemblies = world.get_component(Assembly)
        part_identities = world.get_component(PartIdentity)
        script_behaviors = world.get_component(ScriptBehavior)
        thruster_behaviors = world.get_component(ThrusterBehavior)
        accelerations = world.get_component(Acceleration)
        angular_accelerations = world.get_component(AngularAcceleration)
        rcs_behaviors = world.get_component(RCSBehavior)

        for assembly_eid, assembly in assemblies.items():

            ## PRODUCE
            # Run scripts
            for part_eid in assembly.parts:
                if part_eid in script_behaviors:
                    sb = script_behaviors[part_eid]
                    outputs = sb.script.update(assembly_eid, world, dt)
                    if outputs and part_eid in part_identities:
                        pi = part_identities[part_eid]
                        for script_port, value in outputs.items():
                            real_port = sb.port_mapping.get(script_port, script_port)
                            if real_port in pi.port_values:
                                pi.port_values[real_port] = value



            ## TRANSMIT
            # Propagate edges
            for from_eid, from_port, to_eid, to_port in assembly.edges:
                if from_eid in part_identities and to_eid in part_identities:
                    value = part_identities[from_eid].port_values.get(from_port)
                    if to_port in part_identities[to_eid].port_values:
                        part_identities[to_eid].port_values[to_port] = value



            ## CONSUME

            # Run thruster behaviors
            for part_eid in assembly.parts:
                if part_eid in thruster_behaviors and part_eid in part_identities:
                    tb = thruster_behaviors[part_eid]
                    pi = part_identities[part_eid]
                    throttle = pi.port_values.get(tb.control_port, 0.0)
                    if throttle is not None and assembly_eid in accelerations:
                        acc = accelerations[assembly_eid]
                        acc.x += throttle * tb.max_thrust

            # Run RCS behaviors
            for part_eid in assembly.parts:
                if part_eid in rcs_behaviors and part_eid in part_identities:
                    rb = rcs_behaviors[part_eid]
                    pi = part_identities[part_eid]
                    control = pi.port_values.get(rb.attitude_port)
                    if control is not None and assembly_eid in angular_accelerations:
                        ang_acc = angular_accelerations[assembly_eid]
                        ang_acc.z += control * rb.max_torque