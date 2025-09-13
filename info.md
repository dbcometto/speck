# Notes
Tests require installing the root as a package:
```bash
pip install -e .
```

## Next Steps:
Fix gravity unit test... not sure what's up with it.  Then finish testing the systems and start working on the renderer.


## TODO
- [ ] Make physics perform better for large numbers of entities
- [ ] Finish adding tests 



## Status

### World: 
- Holds everything
- Saving and loading works
- Random asteroid field generation

### Entities: 
- Should be just an ID and some components... but right now also subclasses.  
- **TODO**: Subclasses need to be replaced with factory functions

### Components: 
- All the data, with no logic
- Also a list of component types for saving/loading

### Systems:
- Handles all the logic
- Organized into groups
- Rendering is currently included
- Efficient gravity is implemented

### Unit Tests
- with `pytest`
- Most things are "tested" but not the systems, the only thing that really needs to be tested...



## Issues

### Rendering
- Currently handled as a system... not ideal
- In Matplotlib... cannot handle asteroid field, but good enough for a few test entities
- Pyglet is a good option




## ChatGPT Roadmap?

### Speck Automation Playground Roadmap

#### Phase 1 – Foundations (current → ~1–2 weeks)

**Goal:** Make the universe feel alive and entities autonomous.

- Introduce diverse entity types: wanderers, orbiters, resource collectors.
- Implement sensors: proximity, collision, resource detection.
- Implement actuators: thrusters (multi-directional optional), simple signal output.
- Introduce resource entities: floating energy or mass blobs.
- Implement basic behaviors: wander, chase/avoid, gather resources.
- Optional: simple reproduction—spawn new entities when energy threshold is reached.
- Visualization/debug: color-code states, show sensor ranges, show resource locations.

**Result:** A small but lively sandbox where entities move, interact, and respond to their environment.

---

#### Phase 2 – Automation & Feedback Loops (~2–4 weeks)

**Goal:** Entities start forming emergent patterns and self-sustaining behaviors.

- Expand behavior primitives: conditional actions, simple state machines.
- Implement energy/mass economy: entities consume resources to move, act, reproduce.
- Add event/signaling system: entities can communicate locally or globally.
- Introduce competition/cooperation dynamics: entities can compete for resources or cluster to coordinate.
- Introduce basic persistence: save/load ecosystem state.
- Optional: entity mutation parameters for evolution experimentation.

**Result:** Emergent behaviors appear—clusters, population cycles, resource-driven reproduction.

---

#### Phase 3 – Solar System Integration (~4–8 weeks)

**Goal:** Add orbital mechanics and a rich environment.

- Implement gravity fields: planets, moons, resource asteroids.
- Entities can orbit or navigate planets/asteroids.
- Resource placement follows orbits or gravitational influence.
- Add directional sensors/thrusters for better navigation.
- Optional: add small hazards—collisions, radiation zones, or environmental decay.

**Result:** A dynamic solar-system sandbox with navigation challenges and rich interactions.

---

#### Phase 4 – Advanced Automation & Emergent Complexity (~8+ weeks)

**Goal:** Enable true Von Neumann–style automation and experimentation.

- Advanced reproduction/assembly: entities build new entities or resource structures.
- Specialization: distinct robot types (miners, transporters, defenders).
- Programmable logic interface: let users define conditional or procedural behaviors.
- Ecosystem metrics: track populations, resource flow, energy usage.
- Optional: evolution/mutation of behaviors for emergent strategies.

**Result:** Full automation sandbox—players can observe, manipulate, and experiment with self-replicating, self-organizing robotic populations.

---

###### Phase 5 – Player Interaction Layer (optional / ongoing)

**Goal:** Add tools for the player without micromanaging.

- Spawn/clone entities or colonies.
- Adjust parameters globally (gravity strength, resource density, behavior tendencies).
- Visual debugging overlays: resource flow, sensor ranges, energy levels.
- Record/replay simulation runs.