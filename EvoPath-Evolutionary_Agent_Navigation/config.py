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

DNA_LENGTH = 200          # 120 was too few: min path is ~51 moves and an
                          # evolved route wanders, so it needs real headroom

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

# --- Crossover ---
# Genes are time-ordered, so a random single cut point lets any
# opening pair with any ending.
CROSSOVER_ENABLED = True

# --- Mutation ---
# Applied per gene, not per child. 0.01 over 120 genes averages
# about 1.2 mutations per offspring: enough novelty to keep the
# search alive, small enough to preserve good inherited routes.

MUTATION_RATE = 0.02      # 0.01 works; 0.02 explored slightly faster here

# --- Evolution ---
GEN_PAUSE_FRAMES = 6      # brief hold on the finished generation
FAST_SKIP = 6             # frames advanced per tick in fast mode

# --- HUD ---
HUD_BG    = (12, 12, 16)
HUD_H     = 96               # reserved strip at the top of the window
HUD_DIM   = (150, 150, 165)
BEST_C    = (255, 120, 200)   # champion + its path
BANNER_C  = (70, 220, 130)
HUD_DIV = (58, 58, 72)      # vertical rule separating stats from controls

# Live parameter tuning (keys 1-6 at runtime)
MUTATION_STEP = 0.005
POP_STEP      = 20
POP_MIN, POP_MAX = 20, 300
DNA_STEP      = 20
DNA_MIN, DNA_MAX = 60, 400

# --- HUD experiment panel ---
HUD_H     = 96          #  diversity bar + diagnosis + hint rows
WARN_C    = (255, 110, 110)
OK_C      = (120, 220, 160)
BAR_BG    = (40, 40, 52)

STALL_GENS = 18          # generations with no improvement before we call it
DIVERSITY_LOW = 0.35     # below this the gene pool is collapsing