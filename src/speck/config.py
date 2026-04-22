"""Configuration constants"""
import pyglet

# Physics
G = 6.6743e-20 # gravitational constant in km^3/(kg s^2)



# Simulation
MAX_SUBSTEP_DELTA_T = 1.0
MAX_SUBSTEPS = 2000


# User Input
KEYBINDS = {
    "follow": [pyglet.window.key.F],
    "unfollow": [pyglet.window.key.ESCAPE],
    "deselect": [pyglet.window.key.ESCAPE],
    "inspect": [pyglet.window.key.I],
    "toggle_debug_hud": [pyglet.window.key.F3],
    "focus_minimap": [pyglet.window.key.M]
}
SELECTION_TOLERANCE = 15
ZOOM_FACTOR = 1.1

# Rendering
POINT_ICON_RADIUS = 5.0
MIN_BODY_SCREEN_RADIUS = 5.0
SELECT_SQUARE_PADDING = 7.0

# Colors
BACKGROUND_COLOR = "#0A090A"
SELECTED_COLOR = "#FFEC96"
OTHER_COLOR = "#FFFFFF"
GRAY_COLOR = "#707070"
DARK_GRAY_COLOR = "#222222"
MINIMAP_FOCUS_COLOR = "#6DFFFF"

