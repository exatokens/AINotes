---
id: w5-12-the-experiment-running-the-paper-on-itself
title: "The Experiment: Running the Paper on Itself"
week: 5
topic: "Act III: The Many Meanings of GraphRAG"
order: 12
summary: Running MemGraphRAG's own construction pipeline on a dozen passages of the paper itself produced a staircase of thresholds where no rung admits signal without noise.
---

To see how the construction phase behaves on real text, the paper itself was taken as the corpus — a dozen good passages from it — and its own pipeline was run on them: an afternoon with an LLM extracting fact and schema triplets, exactly as prescribed. Twelve passages yielded **38 fact triplets and 27 distinct schemas**; the schema frequency table was built exactly as the paper prescribes, and the counting began.

The champion: $\langle \text{method}, \text{uses}, \text{technique} \rangle$, frequency five — "sun rises." One row down: $\langle \text{process}, \text{causes}, \text{deficiency} \rangle$, frequency three — the schema carrying the paper's entire diagnosis, its three diseases. You would give it a star. And in the long tail at frequency one: the paper's own three agents (its titular machinery), each in a schema of frequency one — sitting exactly beside $\langle \text{work}, \text{licensed-under}, \text{license} \rangle$, the copyright notice. Identical frequency; opposite worth. A counter cannot tell the paper's title from its legal footer — they are the same number.

## Walking the staircase

| Threshold $\tau$ | What survives |
|---|---|
| $\tau = 4$ | One schema of twenty-seven survives — the banality — and its five surviving facts form five disconnected "X uses Y" edges: a shattered graph, itself a textbook case of structural fragmentation |
| $\tau = 3$ | The diagnosis and the architecture return |
| $\tau = 2$ | PageRank walks back in |
| $\tau = 1$ | Readmits the three agents *and* the copyright notice, hand in hand |

There is no rung that gives signal without noise, because signal and noise share the same frequency.

```python
# reproducing the staircase on the paper's own frequency table
from collections import Counter

schemas = (["method uses technique"] * 5 +
           ["process causes deficiency"] * 3 +
           ["extraction-agent extracts triplet"] * 1 +
           ["resolution-agent adjudicates conflict"] * 1 +
           ["memory-agent stores layer"] * 1 +
           ["work licensed-under license"] * 1)   # the copyright notice, freq 1

freq = Counter(schemas)
for tau in [4, 3, 2, 1]:
    survivors = [s for s, c in freq.items() if c >= tau]
    print(f"tau={tau}: {len(survivors)} schema(s) survive -> {survivors}")
# only tau=1 readmits the agents -- and it readmits the license notice too
```

## Why this is not an artifact of a tiny corpus

STEM knowledge is **Zipfian, long-tailed**: the most valuable things live far out in the tail, often said exactly once in a whole textbook — because anything anyone does creates a subfield, and the bridges between fields are, by definition, rare. Granovetter's weak ties: the rare edge is where the new information lives. Equate frequency with importance in such a distribution and you amputate the tail — and the amputation happens at graph-building time. Be as clever as you like at retrieval; you cannot retrieve what was never admitted to the graph.

Fairness demands the counterweight: the paper's own pilot study shows that removing low-frequency triples slightly improves accuracy on their benchmark data, and this small experiment does not refute their tables. It illustrates what their tables cannot show: on a Zipfian technical corpus, frequency and importance are different quantities, and conflating them is a category mistake with unrecoverable consequences.

> **The one thing to remember.** The amputation happens at graph-building time, not at retrieval time — no retrieval trick can recover a triplet that a frequency threshold already discarded. This is the empirical seed of tonight's Critique C.
