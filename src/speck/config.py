"""Configuration constants"""
import pyglet

# Physics
G = 6.6743e-20 # gravitational constant in km^3/(kg s^2)



# Simulation
DT = 1/60
TIMEWARP = 1

MAX_SUBSTEP_DELTA_T = 1.0
MAX_SUBSTEPS = 2000

TIMEWARP_PRESETS = [0, 1, 60, 3600, 86400]






# User Input
KEYBINDS = {
    # Camera Controls
    "move_up": [pyglet.window.key.W],
    "move_left": [pyglet.window.key.A],
    "move_down": [pyglet.window.key.S],
    "move_right": [pyglet.window.key.D],

    # Entity Interaction
    "follow": [pyglet.window.key.F],
    "unfollow": [pyglet.window.key.ESCAPE],
    "deselect": [pyglet.window.key.ESCAPE],
    "inspect": [pyglet.window.key.I],
    "focus_minimap": [pyglet.window.key.M],
    "open_graph": [pyglet.window.key.G],
    "entity_list": [pyglet.window.key.E], # TODO

    # Time controls
    "pause": [pyglet.window.key.SPACE],
    "increase_timewarp": [pyglet.window.key.PERIOD],
    "decrease_timewarp": [pyglet.window.key.COMMA],

    # Other
    "toggle_debug_hud": [pyglet.window.key.F3],
}
SELECTION_TOLERANCE = 15
ZOOM_FACTOR = 1.1
CAMERA_SENSITIVITY = 500.0



# UI
SIDEBAR_ICON_WIDTH = 30 
SIDEBAR_PANEL_WIDTH = 200 
BOTTOM_BAR_HEIGHT = 80
MINIMAP_WIDTH = 220
MINIMAP_HEIGHT = 200
TOP_BAR_HEIGHT = 30

TIMEWARP_BUTTON_WIDTH = 50
TIMEWARP_BUTTON_GAP = 5
TIMEWARP_BUTTON_COUNT = 5
TIMEWARP_PANEL_WIDTH = TIMEWARP_BUTTON_WIDTH * TIMEWARP_BUTTON_COUNT + TIMEWARP_BUTTON_GAP * (TIMEWARP_BUTTON_COUNT - 1)

MIN_INSPECTOR_COL_WIDTH = 80
MAX_INSPECTOR_COL_WIDTH = 150


# Rendering
POINT_ICON_RADIUS = 5.0
MIN_BODY_SCREEN_RADIUS = 5.0
SELECT_SQUARE_PADDING = 7.0

GRID_TARGET_PX = 800
GRID_MAX_LINES = 1000
GRID_MIN_MINOR_PX = 40
SCALE_BAR_TARGET_PX = 150

INSPECTOR_REFRESH_PERIOD = 0.5





# Colors
BACKGROUND_COLOR = "#0A090A"
SELECTED_COLOR = "#FFEC96"
OTHER_COLOR = "#FFFFFF"
GRAY_COLOR = "#707070"
DARK_GRAY_COLOR = "#222222"
ACCENT_COLOR = "#6DFFFF"

MINIMAP_FOCUS_COLOR = ACCENT_COLOR
GRID_MAJOR_COLOR = GRAY_COLOR
GRID_MINOR_COLOR = DARK_GRAY_COLOR
VELOCITY_ARROW_COLOR = ACCENT_COLOR
