# This code uses pyglet to render the game

import pyglet
from pyglet import shapes

from world import World
from entities import Entity
from factories import Factory


class PygletRenderer:
    def __init__(self,world):

        self.world = world

        self.entity_shapes = {}

        # set up renderer
        self.window = pyglet.window.Window(800, 600, "Speck")
        self.batch = pyglet.graphics.Batch()
        

        # Register events
        self.window.push_handlers(
            on_draw=self.on_draw,
        )

    def sync_shapes(self):
        """Create a Pyglet shape for a new entity."""
        for entity in self.world.entities:
            render = entity.get('Render_Data')
            pos = entity.get('Position')
            radius = entity.get('Radius')

            if render and pos and radius:

                pyg_color = (int(render.color[1:3],16),
                             int(render.color[3:5],16),
                             int(render.color[5:7],16))

                if render.shape_type == 'circle':
                    shape = shapes.Circle(pos.x, pos.y, radius=radius.radius, color=pyg_color, batch=self.batch)

                elif render.shape_type == 'rectangle':
                    shape = shapes.Rectangle(pos.x, pos.y, width=radius.radius, height=radius.radius, color=pyg_color, batch=self.batch)

                self.entity_shapes[entity] = shape

    def on_draw(self):
        """Draw all the entities."""
        self.window.clear()
        self.sync_shapes()

        # for entity, shape in self.entity_shapes.items():
        #     pos = entity.get('Position')
        #     if pos:
        #         shape.x = pos.x
        #         shape.y = pos.y

        self.batch.draw()


# Run the app
if __name__ == "__main__":

    world = World()
    e = Factory.create_rock(0,position=(300,300),radius=100)
    world.add_entity(e)

    renderer = PygletRenderer(world)

    pyglet.app.run()
