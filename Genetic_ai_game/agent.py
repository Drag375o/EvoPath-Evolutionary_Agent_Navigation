import random
import config as cfg


# Grid distance: the real number of moves needed, since agents
# only travel in four directions.
def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# True if this cell is inside the grid.
def in_bounds(col, row):
    return 0 <= col < cfg.COLS and 0 <= row < cfg.ROWS


# True if this cell is part of an obstacle.
def is_wall(col, row):
    return (col, row) in cfg.WALL_CELLS


# One individual. Its DNA is a fixed-length sequence of move indices.
class Agent:

    def __init__(self, dna=None):
        # No DNA passed in -> make a random one.
        # DNA passed in -> use it (this is how crossover children are born).
        if dna is None:
            dna = [random.randrange(len(cfg.MOVES))
                   for _ in range(cfg.DNA_LENGTH)]
        self.dna = dna

        self.col, self.row = cfg.START
        self.trail = [cfg.START]     # every cell visited, for drawing
        self.step_index = 0          # which gene we execute next
        self.alive = True            # False once it hits a wall or the edge
        self.reached_goal = False
        self.fitness = 0.0

    # A generation ends when every agent is finished. An agent is finished
    # if it died, arrived, or ran out of genes.
    def finished(self):
        return (not self.alive) or self.reached_goal \
            or self.step_index >= len(self.dna)

    # Execute one gene.
    def step(self):
        if self.finished():
            return

        dcol, drow = cfg.MOVES[self.dna[self.step_index]]
        new_col = self.col + dcol
        new_row = self.row + drow
        self.step_index += 1

        # Walked off the grid or into a wall -> dead, and it does not move.
        if not in_bounds(new_col, new_row) or is_wall(new_col, new_row):
            self.alive = False
            return

        self.col = new_col
        self.row = new_row
        self.trail.append((self.col, self.row))

        if (self.col, self.row) == cfg.GOAL:
            self.reached_goal = True
    
        # How good was this run? Higher is better. Selection uses only this.
    def evaluate(self):
        dist = manhattan((self.col, self.row), cfg.GOAL)

        # Dense base score: always positive, rises steeply near the goal.
        score = 1.0 / (1.0 + dist)

        if self.reached_goal:
            # Flat bonus so arriving beats any near-miss outright,
            # plus a speed bonus so short paths beat long ones.
            leftover = len(self.dna) - self.step_index
            score += cfg.GOAL_BONUS
            score += (leftover / len(self.dna)) * cfg.SPEED_BONUS
        elif not self.alive:
            # Crashing is bad, but distance covered still counts.
            score *= cfg.DEATH_PENALTY

        self.fitness = score
        return score