---
id: w5-14-three-critiques-preserve-then-decide
title: "Three Critiques, One Disease: Preserve, Then Decide"
week: 5
topic: "Act III: The Many Meanings of GraphRAG"
order: 14
summary: MemGraphRAG indicts isolated extraction for destroying information, then commits the same sin three times at construction time — the fix is to defer judgment to query time.
---

The paper is impressive — the ideas are clean, the diagnosis is real, and the machinery (conflict taxonomy, candidate-to-stable promotion, hub suppression, information density) is genuinely nice. A fair reading credits before it cuts. Three critiques, then the through-line.

## Critique A: "grounding" is a category error

Return to the irreconcilable conflict: Joe born in Berkeley, Joe born in Fremont, no third passage to adjudicate. The resolution agent must pick one — its design always resolves. It is sold as principled: fetch the provenance passages, let the evidence decide. But a passage is not truth — a passage is more text, with unmodeled reliability. "Grounded" means traceable to *some* text, never traceable to *true* text. When the passages underdetermine the answer, the LLM judge's parametric priors lean it to one side — the judge stops reading and starts remembering. That calls for human-in-the-loop review, not silent adjudication. Underneath sits a correlated-errors problem: all three agents run on the same underlying LLM, so the verifier shares the generator's blind spots — the "society of agents" is one model wearing three prompts.

## Critique B: contradictions should be first-class citizens

Discovered contradictions are gems, not noise to be averaged away — two departments reporting different revenue for the same quarter is a finding, not an error. The paper's own taxonomy convicts it: of its three conflict types, two are not even contradictions. Temporal facts are both true, time-indexed — resolving destroys the index. Granularity pairs form an abstraction hierarchy — the honest move is a subsumption edge, which enriches the graph. Only mutually-exclusive is genuine contradiction, so the resolution agent discards true information in two of its own three cases. *They built a seismograph and wired it to erase earthquakes from the record.* The fix costs almost nothing: let detection annotate — a conflicts-with edge, both provenances, a confidence, a temporal validity — instead of letting resolution delete. Don't resolve the contradiction; promote it.

## Critique C: frequency is not importance

The self-experiment proved this by construction. In the construction half, frequency is signal — recurring schemas promoted, rare ones executed. In the retrieval half, frequency is noise — hub suppression penalizes the common, IDF rewards the rare, the mean-not-sum in $P_{init}(e)$ refuses to reward repetition. Two opposite theories of value in one system: the retrieval side would boost the very gem the construction side already erased.

```python
# the irony of Critique C, made concrete
construction_view = {"schema": "process causes deficiency", "frequency": 3, "verdict": "promoted (signal)"}
retrieval_view    = {"entity": "rare cross-domain bridge",   "frequency": 1, "verdict": "would be boosted by IDF (signal)"}

# but the rare bridge in retrieval_view was never admitted to the graph in the first place --
# construction already amputated it at tau >= 2, so retrieval never gets the chance to reward it
print("construction promotes by frequency:", construction_view)
print("retrieval would reward rarity, if only it survived construction:", retrieval_view)
```

## The through-line

Three critiques, one disease. The paper indicts GraphRAG for throwing information away in isolated local extraction — and then commits the same sin three times: a single adjudicated truth (the conflict erased), a single surviving fact (the loser erased), a single frequent schema set (the rare erased). Each is an eager, information-destroying commitment made at construction time — the moment with the *least* context — when it could be deferred to query time, the moment with the *most*.

> **The one thing to remember.** Preserve, then decide. Keep the conflict. Keep the rare. Defer judgment to the moment with the most relevant context. A paper about not losing information should not lose the most interesting information it finds.
