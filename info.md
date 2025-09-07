# Notes

## TODO
- [ ] Fix factory functions  
- [ ] Pull Matplotlib renderer out into a renderer file
- [ ] Replace Matplotlib with Pyglet


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




## Issues

### Rendering
- Currently handled as a system... not ideal
- In Matplotlib... cannot handle asteroid field, but good enough for a few test entities