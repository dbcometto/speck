# speck/ssh/commands.py
import ast


def cmd_agents(world) -> str:
    from ..components.functional import Identity
    from ..components.dynamics import Position
    
    identities = world.get_component(Identity)
    positions  = world.get_component(Position)
    
    lines = []
    for eid, identity in identities.items():
        if identity.classification != "Agent":
            continue
        pos = positions.get(eid)
        pos_str = f"({pos.x:.1f}, {pos.y:.1f})" if pos else "unknown"
        lines.append(f"[{eid}] {identity.name} @ {pos_str}")
    
    return '\n'.join(lines) if lines else "no agents"


def cmd_write(world, key, value_str) -> str:
    try:
        value = ast.literal_eval(value_str)
        world.message_network.write(key, value)
        return f"wrote {key} = {value}"
    except ValueError as e:
        return f"error: invalid value — {e}"