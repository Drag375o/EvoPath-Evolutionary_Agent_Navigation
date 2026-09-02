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
        self.scored = False

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