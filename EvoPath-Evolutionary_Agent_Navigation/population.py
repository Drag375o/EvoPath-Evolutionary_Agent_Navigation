import random
import config as cfg
from agent import Agent


# A group of agents that are simulated together, one generation at a time.
class Population:

    def __init__(self, size=None):
        if size is None:
            size = cfg.POP_SIZE
        self.size = size
        self.agents = [Agent() for _ in range(size)]
        self.generation = 1
        self.scored = False          # has this generation been evaluated yet

    # Advance every agent by one gene.
    def step(self):
        for agent in self.agents:
            agent.step()

    # True once every agent has died, arrived, or run out of genes.
    def all_finished(self):
        return all(agent.finished() for agent in self.agents)

    def count_alive(self):
        return sum(1 for a in self.agents if a.alive and not a.reached_goal)

    def count_dead(self):
        return sum(1 for a in self.agents if not a.alive)

    def count_reached(self):
        return sum(1 for a in self.agents if a.reached_goal)

    # Score every agent, then sort best-first so agents[0] is the champion.
    def evaluate(self):
        for agent in self.agents:
            agent.evaluate()
        self.agents.sort(key=lambda a: a.fitness, reverse=True)

    def best(self):
        return self.agents[0]

    # Roulette-wheel selection: pick one agent at random, weighted by
    # fitness. Better agents are likelier, but weak ones keep a small
    # chance -- that preserves the diversity crossover needs.
    def select_parent(self):
        total = sum(a.fitness for a in self.agents)

        # Degenerate case: if every fitness is 0, fall back to uniform.
        if total <= 0:
            return random.choice(self.agents)

        pick = random.uniform(0, total)
        running = 0.0
        for agent in self.agents:
            running += agent.fitness
            if running >= pick:
                return agent
        return self.agents[-1]      # float rounding safety net

    # The elite: top performers copied forward untouched, so the best
    # solution found so far can never be lost.
    def elites(self):
        return self.agents[:cfg.ELITE_COUNT]

    # Single-point crossover: child inherits the opening moves from one
    # parent and the closing moves from the other. This is where new
    # routes come from -- selection alone can only copy.
    def crossover(self, parent_a, parent_b):
        length = len(parent_a.dna)

        if not cfg.CROSSOVER_ENABLED:
            return list(parent_a.dna)

        # Cut strictly inside the sequence so both parents contribute.
        cut = random.randint(1, length - 1)
        return parent_a.dna[:cut] + parent_b.dna[cut:]
    
    # Randomly replace individual genes. This is the only source of
    # genuinely new genetic material -- crossover can only reshuffle
    # genes that already exist in the population.
    def mutate(self, dna):
        num_moves = len(cfg.MOVES)
        for i in range(len(dna)):
            if random.random() < cfg.MUTATION_RATE:
                dna[i] = random.randrange(num_moves)
        return dna

    # Build the next generation: elites carried over untouched, the rest
    # bred by roulette selection + crossover + mutation.
    def next_generation(self):
        new_agents = []

        # Elites: same DNA, fresh body (position, trail, counters reset).
        for elite in self.elites():
            new_agents.append(Agent(dna=list(elite.dna)))

        # Fill the remainder with children.
        while len(new_agents) < self.size:
            parent_a = self.select_parent()
            parent_b = self.select_parent()
            child_dna = self.mutate(self.crossover(parent_a, parent_b))
            new_agents.append(Agent(dna=child_dna))

        self.agents = new_agents
        self.generation += 1
        self.scored = False

    def average_fitness(self):
        if not self.agents:
            return 0.0
        return sum(a.fitness for a in self.agents) / len(self.agents)

    # Fraction of gene slots where the population still disagrees.
    # 1.0 = every direction present at every position (fully diverse).
    # Near 0 = agents are clones, so crossover produces nothing new.
    def diversity(self):
        if not self.agents:
            return 0.0
        length = len(self.agents[0].dna)
        total = 0
        for i in range(length):
            seen = set()
            for a in self.agents:
                seen.add(a.dna[i])
            total += len(seen)
        return total / (length * len(cfg.MOVES))