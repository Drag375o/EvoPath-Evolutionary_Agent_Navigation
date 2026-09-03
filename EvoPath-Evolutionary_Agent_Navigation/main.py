import pygame
import config as cfg
from population import Population


def draw_cell(surface, col, row, colour, oy=0):
    rect = pygame.Rect(col * cfg.CELL, row * cfg.CELL + oy, cfg.CELL, cfg.CELL)
    pygame.draw.rect(surface, colour, rect)


def draw_grid(surface, oy):
    for x in range(0, cfg.WIDTH, cfg.CELL):
        pygame.draw.line(surface, cfg.GRID, (x, oy), (x, cfg.HEIGHT + oy))
    for y in range(0, cfg.HEIGHT + 1, cfg.CELL):
        pygame.draw.line(surface, cfg.GRID, (0, y + oy), (cfg.WIDTH, y + oy))


def draw_world(surface, oy):
    draw_grid(surface, oy)
    for (col, row, w, h) in cfg.OBSTACLES:
        rect = pygame.Rect(col * cfg.CELL, row * cfg.CELL + oy,
                           w * cfg.CELL, h * cfg.CELL)
        pygame.draw.rect(surface, cfg.WALL, rect)
    draw_cell(surface, cfg.START[0], cfg.START[1], cfg.START_C, oy)
    draw_cell(surface, cfg.GOAL[0], cfg.GOAL[1], cfg.GOAL_C, oy)


def agent_colour(agent):
    if agent.reached_goal:
        return cfg.REACHED_C
    if not agent.alive:
        return cfg.DEAD_C
    return cfg.AGENT_C


# The champion's route: the visual proof that evolution found a path.
def draw_best_path(surface, agent, oy):
    if agent is None or len(agent.trail) < 2:
        return
    points = [(c * cfg.CELL + cfg.CELL // 2,
               r * cfg.CELL + cfg.CELL // 2 + oy) for (c, r) in agent.trail]
    pygame.draw.lines(surface, cfg.BEST_C, False, points, 2)


def draw_population(surface, pop, oy):
    inset, size = 6, cfg.CELL - 12
    order = sorted(pop.agents, key=lambda a: (a.alive, a.reached_goal))
    for agent in order:
        x = agent.col * cfg.CELL + inset
        y = agent.row * cfg.CELL + inset + oy
        pygame.draw.rect(surface, agent_colour(agent),
                         pygame.Rect(x, y, size, size))


# Small horizontal bar, used for the diversity readout.
def draw_bar(surface, x, y, w, h, frac, colour):
    pygame.draw.rect(surface, cfg.BAR_BG, pygame.Rect(x, y, w, h))
    fill = max(0, min(w, int(w * frac)))
    pygame.draw.rect(surface, colour, pygame.Rect(x, y, fill, h))


# Turn the raw numbers into a plain-language verdict about what the
# algorithm is doing right now. This is the point of the experiment:
# the failure modes are visible, not just described.
def diagnose(pop, div, stall, first_gen, best_hist):
    if cfg.MUTATION_RATE <= 0.0001 and stall >= 6:
        return ("STALLED: mutation 0, no new genes -- premature convergence",
                cfg.WARN_C)
    if div < cfg.DIVERSITY_LOW and first_gen is None and stall >= cfg.STALL_GENS:
        return ("STALLED: gene pool collapsed -- premature convergence",
                cfg.WARN_C)
    if stall >= cfg.STALL_GENS and first_gen is None:
        return ("no improvement for %d generations -- search is stuck" % stall,
                cfg.WARN_C)
    if cfg.MUTATION_RATE > 0.030 and len(best_hist) >= 6:
        window = best_hist[-6:]
        if max(window) - min(window) > 1.0:
            return ("UNSTABLE: mutation too high -- good routes destroyed",
                    cfg.WARN_C)
    if first_gen is not None:
        return ("GOAL REACHED  --  first solved at generation %d" % first_gen,
                cfg.BANNER_C)
    return ("searching... fitness climbing, diversity healthy", cfg.HUD_DIM)


# Stats passed in are from the last COMPLETED generation, so the numbers
# stay readable instead of blanking to zero while a new generation runs.
def draw_hud(surface, font, small, tiny, pop, state):
    pygame.draw.rect(surface, cfg.HUD_BG,
                     pygame.Rect(0, 0, cfg.WIDTH, cfg.HUD_H))

    # Row 1 -- headline numbers.
    row1 = "Gen %d      Best %.3f      Best ever %.3f      Avg %.3f" % (
        pop.generation, state["last_best"], state["best_ever"],
        state["last_avg"])
    surface.blit(font.render(row1, True, cfg.TEXT), (12, 8))

    # Row 2 -- population state and live parameters.
    row2 = "agents %d  reached %d  dead %d  |  pop %d  mut %.3f  dna %d" % (
        len(pop.agents), state["last_reached"], pop.count_dead(),
        cfg.POP_SIZE, cfg.MUTATION_RATE, cfg.DNA_LENGTH)
    surface.blit(small.render(row2, True, cfg.HUD_DIM), (12, 32))

    # Row 3 -- gene pool diversity, the thing mutation controls.
    div = state["diversity"]
    div_c = cfg.WARN_C if div < cfg.DIVERSITY_LOW else cfg.OK_C
    surface.blit(small.render("diversity", True, cfg.HUD_DIM), (12, 52))
    draw_bar(surface, 92, 55, 110, 9, div, div_c)
    surface.blit(small.render("%.2f" % div, True, div_c), (212, 52))
    if state["stall"]:
        surface.blit(small.render("no gain for %d gens" % state["stall"],
                                  True, cfg.HUD_DIM), (268, 52))

    # Row 4 -- status, then mode flags after a divider.
    msg, msg_c = state["diagnosis"]
    surface.blit(small.render(msg, True, msg_c), (12, 74))

    flags = []
    if state["fast"]:
        flags.append("FAST")
    if state["paused"]:
        flags.append("PAUSED")
    if flags:
        x = 12 + small.size(msg)[0] + 10
        surface.blit(small.render("|  " + "  ".join(flags), True,
                                  cfg.AGENT_C), (x, 74))

    # Vertical rule: live stats on the left, static reference on the right.
    panel_x = cfg.WIDTH - 250
    pygame.draw.line(surface, cfg.HUD_DIV,
                     (panel_x, 4), (panel_x, cfg.HUD_H - 4), 1)

    # Top-right panel: controls and the parameter experiment, kept tiny
    # so they stay out of the way of the live numbers.
    lines = [
        ("[F]ast   [Space]pause   [R]estart", cfg.HUD_DIM),
        ("1/2 pop    3/4 mutation    5/6 dna", cfg.HUD_DIM),
        ("EXPERIMENT  (change, then [R])", cfg.AGENT_C),
        ("3 x4 -> 0.000 = stalls, no new genes", cfg.AGENT_C),
        ("4 x6 -> 0.050 = unstable, routes lost", cfg.AGENT_C),
    ]
    right = cfg.WIDTH - 14
    y = 6
    for text, colour in lines:
        img = tiny.render(text, True, colour)
        surface.blit(img, (right - img.get_width(), y))
        y += 16


def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT + cfg.HUD_H))
    pygame.display.set_caption("Evolutionary Pathfinding with Genetic Algorithms")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 17)
    small = pygame.font.SysFont("consolas", 14)
    tiny = pygame.font.SysFont("consolas", 11)
    oy = cfg.HUD_H

    def fresh():
        return {
            "best_ever": 0.0, "last_best": 0.0, "last_avg": 0.0,
            "last_reached": 0, "first_gen": None, "diversity": 1.0,
            "stall": 0, "best_hist": [],
            "diagnosis": ("searching...", cfg.HUD_DIM),
            "fast": False, "paused": False,
        }

    pop = Population()
    state = fresh()
    best_agent = None
    pause = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    running = False
                elif k == pygame.K_f:
                    state["fast"] = not state["fast"]
                elif k == pygame.K_SPACE:
                    state["paused"] = not state["paused"]
                elif k == pygame.K_r:
                    pop = Population()
                    keep_fast = state["fast"]
                    state = fresh()
                    state["fast"] = keep_fast
                    best_agent = None
                # Parameters apply from the next [R] restart onward.
                elif k == pygame.K_1:
                    cfg.POP_SIZE = max(cfg.POP_MIN, cfg.POP_SIZE - cfg.POP_STEP)
                elif k == pygame.K_2:
                    cfg.POP_SIZE = min(cfg.POP_MAX, cfg.POP_SIZE + cfg.POP_STEP)
                elif k == pygame.K_3:
                    cfg.MUTATION_RATE = max(0.0, cfg.MUTATION_RATE - cfg.MUTATION_STEP)
                elif k == pygame.K_4:
                    cfg.MUTATION_RATE = min(0.5, cfg.MUTATION_RATE + cfg.MUTATION_STEP)
                elif k == pygame.K_5:
                    cfg.DNA_LENGTH = max(cfg.DNA_MIN, cfg.DNA_LENGTH - cfg.DNA_STEP)
                elif k == pygame.K_6:
                    cfg.DNA_LENGTH = min(cfg.DNA_MAX, cfg.DNA_LENGTH + cfg.DNA_STEP)

        if not state["paused"]:
            for _ in range(cfg.FAST_SKIP if state["fast"] else 1):
                if not pop.all_finished():
                    pop.step()
                    continue
                if not pop.scored:
                    pop.evaluate()
                    pop.scored = True

                    state["last_best"] = pop.best().fitness
                    state["last_avg"] = pop.average_fitness()
                    state["last_reached"] = pop.count_reached()
                    state["diversity"] = pop.diversity()
                    state["best_hist"].append(state["last_best"])

                    # Stall counter: generations since best-ever improved.
                    if state["last_best"] > state["best_ever"] + 1e-9:
                        state["best_ever"] = state["last_best"]
                        state["stall"] = 0
                    else:
                        state["stall"] += 1

                    if state["first_gen"] is None and state["last_reached"] > 0:
                        state["first_gen"] = pop.generation

                    state["diagnosis"] = diagnose(
                        pop, state["diversity"], state["stall"],
                        state["first_gen"], state["best_hist"])

                    best_agent = pop.best()      # keep its trail to draw
                    pause = cfg.GEN_PAUSE_FRAMES
                elif pause > 0:
                    pause -= 1
                else:
                    pop.next_generation()

        screen.fill(cfg.BG)
        draw_world(screen, oy)
        draw_best_path(screen, best_agent, oy)
        draw_population(screen, pop, oy)
        draw_hud(screen, font, small, tiny, pop, state)
        pygame.display.flip()
        clock.tick(cfg.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()