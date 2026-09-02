# config.py — every tunable number in the project lives here.

# --- Grid / window ---
CELL = 20                 # pixel size of one grid cell
COLS = 40
ROWS = 30
WIDTH = COLS * CELL       # 800
HEIGHT = ROWS * CELL      # 600
FPS = 30

# --- World layout (in grid cells, not pixels) ---
START = (2, 15)
GOAL = (37, 15)

# Each obstacle: (col, row, width_in_cells, height_in_cells)
OBSTACLES = [
    (12, 0, 2, 11),       # wall from the top, gap below it
    (12, 19, 2, 11),      # wall from the bottom -> gap in the middle
    (24, 8, 2, 22),       # wall from the bottom -> gap along the top
]

# --- Colours ---
BG       = (18, 18, 24)
GRID     = (32, 32, 42)
WALL     = (90, 95, 110)
START_C  = (80, 170, 255)
GOAL_C   = (70, 220, 130)
TEXT     = (230, 230, 235)



# --- Agent ---
# Move table. DNA stores indices into this list.
# 0 = up, 1 = down, 2 = left, 3 = right
MOVES = [(0, -1), (0, 1), (-1, 0), (1, 0)]

DNA_LENGTH = 120          # how many moves each agent gets

AGENT_C = (255, 180, 60)
TRAIL_C = (110, 80, 40)

# --- Population ---
POP_SIZE = 100



# Precomputed set of every cell occupied by a wall.
# Turns collision into a single O(1) set lookup instead of looping
# over every obstacle rectangle on every move of every agent.
WALL_CELLS = set()
for (_c, _r, _w, _h) in OBSTACLES:
    for _dc in range(_w):
        for _dr in range(_h):
            WALL_CELLS.add((_c + _dc, _r + _dr))

# --- Agent state colours ---
DEAD_C    = (95, 70, 70)      # hit a wall or the edge
REACHED_C = (120, 255, 180)   # made it to the goal

# --- Fitness ---
GOAL_BONUS  = 10.0    # flat reward for arriving
SPEED_BONUS = 5.0     # extra, scaled by how many genes were left over
DEATH_PENALTY = 0.7   # fitness multiplier for agents that crashed

# --- Selection ---
ELITE_COUNT = 4    # top agents copied unchanged into the next generation