import config as cfg
from population import Population

pop = Population()
parent = pop.agents[0]

# Mutate a copy many times and count how many genes actually changed.
total_changed = 0
trials = 500

for _ in range(trials):
    original = list(parent.dna)
    mutated = pop.mutate(list(original))

    assert len(mutated) == len(original), "length changed"
    for gene in mutated:
        assert 0 <= gene < len(cfg.MOVES), "invalid gene produced"

    total_changed += sum(1 for i in range(len(original))
                         if original[i] != mutated[i])

avg = total_changed / trials
expected = cfg.MUTATION_RATE * cfg.DNA_LENGTH * 0.75

print("mutation rate      ", cfg.MUTATION_RATE)
print("dna length         ", cfg.DNA_LENGTH)
print("avg genes changed  ", round(avg, 2))
print("expected (approx)  ", round(expected, 2))
print()
print("all", trials, "mutants had valid length and valid genes")