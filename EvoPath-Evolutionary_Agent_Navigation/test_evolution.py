import config as cfg
from population import Population
from agent import manhattan


def diversity(pop):
    # Fraction of gene positions where the population disagrees.
    # 0.0 = every agent identical (converged). Higher = more variety.
    unique = 0
    for i in range(cfg.DNA_LENGTH):
        seen = set(a.dna[i] for a in pop.agents)
        unique += len(seen)
    return unique / (cfg.DNA_LENGTH * len(cfg.MOVES))


def run(generations, label, dna_length=None, mutation=None, elites=None):
    if dna_length is not None:
        cfg.DNA_LENGTH = dna_length
    if mutation is not None:
        cfg.MUTATION_RATE = mutation
    if elites is not None:
        cfg.ELITE_COUNT = elites

    pop = Population()
    best_ever = 0.0
    best_dist = 999
    first_reach = None

    print()
    print("=== %s ===" % label)
    print("  dna=%d  mutation=%.3f  elites=%d"
          % (cfg.DNA_LENGTH, cfg.MUTATION_RATE, cfg.ELITE_COUNT))
    print("gen   best_fit   closest   reached   stranded   diversity")

    for gen in range(1, generations + 1):
        while not pop.all_finished():
            pop.step()
        pop.evaluate()

        top = pop.best()
        dist = min(manhattan((a.col, a.row), cfg.GOAL) for a in pop.agents)
        stranded = sum(1 for a in pop.agents if a.alive and not a.reached_goal)
        div = diversity(pop)

        best_ever = max(best_ever, top.fitness)
        best_dist = min(best_dist, dist)
        if first_reach is None and pop.count_reached() > 0:
            first_reach = gen

        if gen % 15 == 0 or gen == 1:
            print("%-5d %-10.3f %-9d %-9d %-10d %.3f"
                  % (gen, top.fitness, dist, pop.count_reached(),
                     stranded, div))

        pop.next_generation()

    print("  best ever %.3f   closest %d cells   first reached: %s"
          % (best_ever, best_dist, first_reach if first_reach else "never"))


run(100, "current settings", 120, 0.01, 4)
run(100, "higher mutation", 120, 0.03, 4)
run(100, "higher mutation + longer dna", 200, 0.03, 4)