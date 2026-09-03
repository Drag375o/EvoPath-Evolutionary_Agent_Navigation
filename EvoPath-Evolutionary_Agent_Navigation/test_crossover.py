from population import Population

pop = Population()

while not pop.all_finished():
    pop.step()
pop.evaluate()

a = pop.agents[0]
b = pop.agents[1]

child = pop.crossover(a, b)

print("parent A len", len(a.dna))
print("parent B len", len(b.dna))
print("child    len", len(child))
print()

# Find where the child stops matching A and starts matching B.
cut = next(i for i in range(len(child)) if child[i] != a.dna[i]) \
    if child != list(a.dna) else None

print("first 20 genes")
print("  A    ", a.dna[:20])
print("  B    ", b.dna[:20])
print("  child", child[:20])
print()
print("last 20 genes")
print("  A    ", a.dna[-20:])
print("  B    ", b.dna[-20:])
print("  child", child[-20:])
print()

# The real test: every gene must come from the correct parent.
for _ in range(200):
    c = pop.crossover(a, b)
    assert len(c) == len(a.dna), "length changed"
    # Genes must match A up to some point, then B from there on.
    ok = any(c == a.dna[:k] + b.dna[k:] for k in range(1, len(c)))
    assert ok, "child is not a clean single-point splice"

print("200 children checked: all are valid single-point splices")