# Visualization

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import pyglet
import math

from .components import Position, Velocity, Acceleration, Forces
from .components import Radius, Mass
from .components import Thruster
from .components import Behavior_Orbiter
from .components import RenderData
from .entities import Entity




def make_line(x1, y1, x2, y2, thickness=2, color=(255,255,255), batch=None):
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    angle = math.degrees(math.atan2(-dy, dx))
    rect = pyglet.shapes.Rectangle(
        x=x1, y=y1,
        width=length,
        height=thickness,
        color=color,
        batch=batch
    )
    rect.anchor_x = 0           # rotate around left edge
    rect.anchor_y = thickness/2 # vertically center the rectangle
    rect.rotation = angle
    return rect



# Render with pyglet
class RendererPyglet():
    def __init__(self, width=1000, height=600):
        self.width = width
        self.height = height

        # Create window
        self.window = pyglet.window.Window(width=width, height=height, caption="Simulation")
        self.shapes = []

        pyglet.gl.glClearColor(0.035, 0.035, 0.035, 1.0)  # Dark gray

        # Camera offset
        self.camera_x = 0
        self.camera_y = 0
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.zoom = 1.0
        self.zoom_factor = 1.1  # TODO: make config changeable
        self.zoom_bias = 0.15

        # Hook the draw event
        self.window.push_handlers(self)

    # ----- Input handlers -----
    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.is_dragging = True
            self.drag_start_x = x
            self.drag_start_y = y

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.is_dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.is_dragging:
            # Move camera opposite to mouse movement
            self.camera_x -= dx/self.zoom
            self.camera_y -= dy/self.zoom

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        old_zoom = self.zoom
        if scroll_y > 0:
            self.zoom *= self.zoom_factor   # zoom in
        else:
            self.zoom /= self.zoom_factor   # zoom out

        #
        world_x = (x - self.width/2) / old_zoom + self.camera_x
        world_y = (y - self.height/2) / old_zoom + self.camera_y
        dx = (world_x - self.camera_x) * self.zoom_bias
        dy = (world_y - self.camera_y) * self.zoom_bias
        self.camera_x += dx
        self.camera_y += dy




    # ----- Update/draw -----
    def update(self, entities, entities_by_id):
        self.shapes.clear()
        self.batch = pyglet.graphics.Batch()

        half_width  = self.width / (2 * self.zoom)
        half_height = self.height / (2 * self.zoom)
        left   = self.camera_x - half_width
        right  = self.camera_x + half_width
        bottom = self.camera_y - half_height
        top    = self.camera_y + half_height

        for e in entities:
            pos = e.get(Position)
            radius = e.get(Radius)
            render = e.get(RenderData)
            vel = e.get(Velocity)
            thruster = e.get(Thruster)

            if not pos or not render:
                continue

            # --- Determine bounding box in world coordinates ---
            if render.shape == "circle" and radius:
                r_world = radius.radius
                left_bb   = pos.x - r_world
                right_bb  = pos.x + r_world
                bottom_bb = pos.y - r_world
                top_bb    = pos.y + r_world

            elif render.shape == "rectangle" and radius:
                half = radius.radius / 2
                left_bb   = pos.x - half
                right_bb  = pos.x + half
                bottom_bb = pos.y - half
                top_bb    = pos.y + half
            else:
                continue  # skip unknown shapes



            # --- Convert to screen coordinates and render ---
            x = (pos.x - self.camera_x) * self.zoom + self.width / 2
            y = (pos.y - self.camera_y) * self.zoom + self.height / 2
            r = radius.radius * self.zoom

            if render.shape == "circle":
                if not any([right_bb < left, left_bb > right, top_bb < bottom, bottom_bb > top]):
                    circle = pyglet.shapes.Circle(
                        x=x, y=y, radius=r,
                        color=(102, 102, 102),
                        batch=self.batch
                    )
                    self.shapes.append(circle)

            elif render.shape == "rectangle":
                if not any([right_bb < left, left_bb > right, top_bb < bottom, bottom_bb > top]):
                    rect = pyglet.shapes.Rectangle(
                        x=x - r/2,
                        y=y - r/2,
                        width=r,
                        height=r,
                        color=(78, 218, 194),
                        batch=self.batch
                    )
                    self.shapes.append(rect)

                # --- Velocity arrow ---
                if vel:
                    x2 = (pos.x + vel.x*0.6 - self.camera_x) * self.zoom + self.width / 2
                    y2 = (pos.y + vel.y*0.6 - self.camera_y) * self.zoom + self.height / 2
                    # Cull arrow if completely off-screen
                    if not ( (x < 0 and x2 < 0) or (x > self.width and x2 > self.width) or (y < 0 and y2 < 0) or (y > self.height and y2 > self.height) ):
                        line = make_line(
                            x, y, x2, y2,
                            thickness=2,
                            color=(56, 255, 116),
                            batch=self.batch
                        )
                        self.shapes.append(line)

                # --- Thruster arrow ---
                if thruster:
                    x2 = (pos.x - thruster.thrust_x*0.6 - self.camera_x) * self.zoom + self.width / 2
                    y2 = (pos.y - thruster.thrust_y*0.6 - self.camera_y) * self.zoom + self.height / 2
                    # Cull arrow if completely off-screen
                    if not ( (x < 0 and x2 < 0) or (x > self.width and x2 > self.width) or (y < 0 and y2 < 0) or (y > self.height and y2 > self.height) ):
                        line = make_line(
                            x, y, x2, y2,
                            thickness=2,
                            color=(255, 112, 56),
                            batch=self.batch
                        )
                        self.shapes.append(line)

        self.window.clear()
        self.batch.draw()
        self.window.flip()















# Render with matplotlib
class RendererMatplotlib():
    def __init__(self,resolution=(1000,600),dpi=100,zoom_bias=0.2):
        # Config
        # TODO: make this into a config file
        self.resolution = resolution
        self.dpi = dpi
        self.figure_size = (self.resolution[0] / self.dpi, self.resolution[1] / self.dpi)

        self.aspect_ratio = self.resolution[0]/self.resolution[1]
        self.zoom_bias = zoom_bias




        # Set up plotting values
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=self.figure_size,dpi=self.dpi)
        
        self.fig.patch.set_facecolor('#D8D8D8')  # sets the figure background
        self.ax.set_facecolor("#090909")     # sets the axes (plot) background
        
        self.ax.margins(0)
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_xticks([])
        self.ax.set_yticks([])


        # Set limits
        self.ax.set_xlim(-self.resolution[0]/2, self.resolution[0]/2)
        self.ax.set_ylim(-self.resolution[1]/2, self.resolution[1]/2)
        self.fig.canvas.draw_idle()

        # Connect scroll event
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)


        # Update systems
        self.renderSystem = RenderSystemMatplotlib(self.fig,self.ax)


    def update(self, entities, entities_by_id):
        self.renderSystem.update(entities,entities_by_id)


    def on_scroll(self,event):
        zoom_factor = 1.1 if event.button == 'down' else 0.9

        # Mouse position in data coordinates
        xdata = event.xdata
        ydata = event.ydata

        # Current axis limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        x_left, x_right = cur_xlim
        y_bottom, y_top = cur_ylim

        x_center = (x_left + x_right)/2
        y_center = (y_bottom + y_top)/2

        # Shift center fractionally toward mouse
        dx = (xdata - x_center) * self.zoom_bias
        dy = (ydata - y_center) * self.zoom_bias
        new_center_x = x_center + dx
        new_center_y = y_center + dy

        # Current half-ranges
        x_half = (x_right - x_left)/2 * zoom_factor
        y_half = (y_top - y_bottom)/2 * zoom_factor

        # Apply desired aspect ratio
        width = max(x_half * 2, y_half * 2 * self.aspect_ratio) / 2
        height = width / self.aspect_ratio

        
        # Update view
        self.ax.set_xlim(new_center_x - width, new_center_x + width)
        self.ax.set_ylim(new_center_y - height, new_center_y + height)
        self.fig.canvas.draw_idle()




class RenderSystemMatplotlib():
    def __init__(self,fig,ax):
        self.fig = fig
        self.ax = ax

        self.thruster_scale = 1.3
        self.thruster_width = 1.8

        self.vel_scale = 0.6
        self.vel_width = 1.2
        

    def update(self, entities, entities_by_id):
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_position([0, 0, 1, 1])
        self.ax.margins(0)

        for patch in self.ax.patches:
            patch.remove()  

        for e in entities:
            pos = e.get(Position)
            vel = e.get(Velocity)

            radius = e.get(Radius)

            thruster = e.get(Thruster)

            render = e.get(RenderData)

            if pos and radius and render.shape=="circle":
                shape = plt.Circle((pos.x, pos.y), radius.radius, color='#666666')
                self.ax.add_patch(shape)

            if pos and radius and render.shape=="rectangle":
                radius = radius.radius

                if thruster:
                    arrow = FancyArrowPatch((pos.x, pos.y), (pos.x - thruster.thrust_x*self.thruster_scale, pos.y - thruster.thrust_y*self.thruster_scale), arrowstyle='-', mutation_scale=100, color="#FF7038", linewidth=self.thruster_width)
                    self.ax.add_patch(arrow)

                if vel:
                    arrow = FancyArrowPatch((pos.x, pos.y), (pos.x + vel.x*self.vel_scale, pos.y + vel.y*self.vel_scale), arrowstyle='-', mutation_scale=20, color="#38FF74", linewidth=self.vel_width)
                    self.ax.add_patch(arrow)

                shape = plt.Rectangle((pos.x-radius/2, pos.y-radius/2), radius, radius, color="#4EDAC2")
                self.ax.add_patch(shape)

                


        plt.draw()
        self.fig.canvas.flush_events()
        # plt.pause(0.0001)