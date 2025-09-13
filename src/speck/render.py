# Visualization

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch


from .components import Position, Velocity, Acceleration, Forces
from .components import Radius, Mass
from .components import Thruster
from .components import Behavior_Orbiter
from .components import RenderData

from .entities import Entity

class Renderer():
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