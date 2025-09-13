# Notes
Tests require installing the root as a package:
```bash
pip install -e .
```

## Next Steps:
Fix gravity unit test... not sure what's up with it.  Then finish testing the systems and start working on the renderer.


## TODO
- [x] Fix factory functions
- [ ] Pull Matplotlib renderer out into a renderer file
- [ ] Replace Matplotlib with Pyglet
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