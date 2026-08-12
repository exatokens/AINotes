---
id: w5-11-memgraphrag-diseases-and-construction
title: "MemGraphRAG: Three Diseases and a Shared Memory"
week: 5
topic: "Act III: The Many Meanings of GraphRAG"
order: 11
summary: MemGraphRAG diagnoses isolated fragment-level extraction as GraphRAG's root defect, then builds its graph by promoting only schemas whose frequency clears a threshold.
---

MemGraphRAG is the latest advancement in the lineage, and the paper this course gave a full public evening to. The assessment, stated up front: a remarkable idea; in implementation, still a work in progress. It is very good at diagnosing a disease; its core ideas are beautiful; and when the paper's own pipeline was run on itself, something instructive happened (the next page's staircase).

## The diagnosis: one root defect, three diseases

Existing GraphRAG methods, the paper argues, share one root defect: **isolated, fragment-level extraction** — each chunk processed alone, in the dark, with no global view of the corpus. (Community detection builds themes *afterwards*, out of whatever the isolated extractions produced, and hopes for the best.) From that root defect, three diseases:

- **Thematic irrelevance** — off-topic matter carried dutifully into the graph: a copyright notice filed beside the physics as if it were physics.
- **Logical inconsistency** — contradiction: one statement says X, another cannot be reconciled with X, and a naive community summary can end up reading "Napoleon attacked Russia, which was good and bad."
- **Structural fragmentation** — a key idea that never makes it into the graph in one piece, because chunking took a knife to it or it was scattered across documents.

## The cure: shared memory and a society of agents

Two commitments. First, the **shared memory** that gives the paper its name — not RAM, but working memory in the agent-architecture sense: the three layers from Act II (ontology, facts, passages), held together in one persistent, global store that every agent reads and writes while the corpus is processed. Second, a **society of agents**: an extraction agent that reads chunks and extracts all three layers at once (every fact keeping an evidence link to its source passage); a conflict-detection agent scanning the fact layer for contradictions; a conflict-resolution agent adjudicating by scanning the corpus for provenance.

Conflicts fall into a taxonomy of three:

| Conflict type | Example | Resolution |
|---|---|---|
| **Granularity** | John born in Berkeley vs. born in the United States | Not a contradiction — containment |
| **Temporal** | Biden was president; Trump was president | Both true, time-indexed |
| **Mutually exclusive** | Einstein born 1879 vs. 1880 | Only one survives (1879) |

## Building the graph: candidates, promotion, and the jury pool

Construction rests on the typing function $\phi$ from Act II. The extraction agent mines the corpus and fills a staging area — a bucket of **candidate schemas**. Nothing is promoted to the stable pool by default. A schema is promoted only when its empirical frequency across the corpus clears a threshold:

$$\text{Freq}(s) \geq \tau$$

The core thesis, stated baldly: **frequency determines significance**. A recurring ontological pattern is probably important; a rare one is probably noise. Promoted schemas bring their fact triplets with them, and those facts bring their passages. Passages left behind — belonging to no promoted fact — become lone islands the structured retrieval will never reach, though plain RAG can still see them. It is somewhat like jury duty: the candidates never selected are simply let go.

```python
# candidate-to-stable promotion, toy version -- frequency clears a threshold or it doesn't
from collections import Counter

candidate_schemas = [
    "person born-in country", "person born-in country", "person born-in country",
    "person born-in country", "person born-in country",     # freq 5 -- banal but common
    "process causes deficiency", "process causes deficiency", "process causes deficiency",
    "agent extracts triplet",                                 # freq 1 -- the paper's own machinery
    "work licensed-under license",                            # freq 1 -- the copyright notice
]

freq = Counter(candidate_schemas)

for tau in [4, 3, 1]:
    promoted = [s for s, c in freq.items() if c >= tau]
    print(f"tau={tau}: promoted = {promoted}")
# tau=1 admits the paper's own agents -- and the copyright notice, hand in hand
```

> **The one thing to remember.** MemGraphRAG's entire construction phase is a bet that frequency and importance are the same quantity. The next page's self-experiment tests that bet directly, on the paper itself.
