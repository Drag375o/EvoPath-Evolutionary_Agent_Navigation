import pygame
import config as cfg
from population import Population


# Fill a single grid cell.
def draw_cell(surface, col, row, colour):
    rect = pygame.Rect(col * cfg.CELL, row * cfg.CELL, cfg.CELL, cfg.CELL)
    pygame.draw.rect(surface, colour, rect)


# Faint lines so the cell structure is visible.
def draw_grid(surface):
    for x in range(0, cfg.WIDTH, cfg.CELL):
        pygame.draw.line(surface, cfg.GRID, (x, 0), (x, cfg.HEIGHT))
    for y in range(0, cfg.HEIGHT, cfg.CELL):
        pygame.draw.line(surface, cfg.GRID, (0, y), (cfg.WIDTH, y))


# Background, grid, obstacles, start and goal.
def draw_world(surface):
    surface.fill(cfg.BG)
    draw_grid(surface)

    for (col, row, w, h) in cfg.OBSTACLES:
        rect = pygame.Rect(col * cfg.CELL, row * cfg.CELL,
                           w * cfg.CELL, h * cfg.CELL)
        pygame.draw.rect(surface, cfg.WALL, rect)

    draw_cell(surface, cfg.START[0], cfg.START[1], cfg.START_C)
    draw_cell(surface, cfg.GOAL[0], cfg.GOAL[1], cfg.GOAL_C)


# Colour tells you the agent's state at a glance.
def agent_colour(agent):
    if agent.reached_goal:
        return cfg.REACHED_C
    if not agent.alive:
        return cfg.DEAD_C
    return cfg.AGENT_C


# Dead agents first, so living ones and winners draw on top of them.
def draw_population(surface, pop):
    inset = 6
    size = cfg.CELL - inset * 2

    order = sorted(pop.agents,
                   key=lambda a: (a.alive, a.reached_goal))

    for agent in order:
        x = agent.col * cfg.CELL + inset
        y = agent.row * cfg.CELL + inset
        pygame.draw.rect(surface, agent_colour(agent),
                         pygame.Rect(x, y, size, size))


def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    clock = pygame.time.Clock()

    pop = Population()

    running = True
    while running:
        # 1. Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    pop = Population()     # fresh random population

        # 2. Update
        pop.step()
        if pop.all_finished() and not pop.scored:
            pop.evaluate()
            pop.scored = True

        # 3. Draw
        draw_world(screen)
        draw_population(screen, pop)

        # Counts in the title bar -- proper on-screen text comes in Stage 10.
        best_fit = pop.best().fitness if pop.scored else 0.0
        pygame.display.set_caption(
            "Gen %d   |   alive %d   dead %d   reached %d   |   best fitness %.3f"
            % (pop.generation, pop.count_alive(), pop.count_dead(),
               pop.count_reached(), best_fit)
        )

        pygame.display.flip()
        clock.tick(cfg.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()