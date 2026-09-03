from population import Population
from collections import Counter

pop = Population()

# Run one full generation.
while not pop.all_finished():
    pop.step()
pop.evaluate()

print("best fitness   ", round(pop.best().fitness, 4))
print("worst fitness  ", round(pop.agents[-1].fitness, 4))
print("elite fitnesses", [round(a.fitness, 4) for a in pop.elites()])

# Draw 10000 parents and see who actually gets picked.
picks = Counter()
for _ in range(10000):
    picks[id(pop.select_parent())] += 1

print()
print("rank  fitness   times picked out of 10000")
for rank, agent in enumerate(pop.agents[:5]):
    print("  %-4d %-9.4f %d" % (rank, agent.fitness, picks[id(agent)]))
for rank in (len(pop.agents) - 2, len(pop.agents) - 1):
    agent = pop.agents[rank]
    print("  %-4d %-9.4f %d" % (rank, agent.fitness, picks[id(agent)]))
    