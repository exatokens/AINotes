---
id: w5-14-three-critiques-preserve-then-decide
title: "Three Critiques, One Disease: Preserve, Then Decide"
week: 5
topic: "Act III: The Many Meanings of GraphRAG"
order: 14
summary: MemGraphRAG indicts isolated extraction for destroying information, then commits the same sin three times at construction time — the fix is to defer judgment to query time.
---

The paper is impressive — the ideas are clean, the diagnosis is real, and the machinery (conflict taxonomy, candidate-to-stable promotion, hub suppression, information density) is genuinely nice. A fair reading credits before it cuts. Three critiques, then the through-line.

## Core intuition

The most important thing in a graph-constructed system is not whether it can be made elegant, but whether it preserves the information needed for a good answer.

A graph that deletes conflicts, erases rare facts, or resolves ambiguity too early is throwing away the very structure the system should exploit.

## Why it matters

This is the recurring design principle of the whole course: preserve the information, then decide how to use it. Construction-time commitment is the most dangerous place to do it, because that is when the knowledge is least context-rich.

## Instructor framing

The through-line ("preserve, then decide") is one of the most transferable ideas in the entire course — it applies far beyond GraphRAG, to chunking (Week 3's "don't resolve ambiguity, keep the context"), to guardrails (Week 6), to any system design where a decision must be made under incomplete information. Have students articulate the general principle before the GraphRAG-specific instance, so it travels with them into other systems they'll design later.

## Worked example



Take the Joe-born-in-Berkeley-versus-Fremont example literally. MemGraphRAG's resolution agent, facing two irreconcilable facts with no third passage to break the tie, must output exactly one — its architecture has no "I don't know, and here is why" state. Suppose the underlying LLM's training data happened to contain more mentions of a different, more famous Joe born in Fremont; the resolution agent's parametric prior nudges it there, and the graph now states, with the same confident formatting as every other fact, "Joe was born in Fremont" — indistinguishable from a fact the corpus actually supports unanimously. A downstream user asking "where was Joe born" gets a single, unhedged answer with no visible trace that the underlying evidence was ever contested. Compare this to the alternative the critique proposes: annotate both claims with a "conflicts-with" edge, both provenances attached, and let the *querying* system (or a human) decide how to handle the ambiguity with full information — a strictly more informative graph, at essentially no extra construction cost.

This chapter moves from praising the paper to diagnosing its design trade-offs. The sharpest critique is not that the system is wrong, but that it is too eager to compress before the right context exists.

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






## Math explained step by step

Formalize Critique C's "irony" precisely — it is not merely a rhetorical flourish, it is a provable inconsistency between two stages of the same pipeline.

**Step 1 — state construction's implicit value function.** Construction promotes schema $s$ if $\text{Freq}(s) \geq \tau$ — value is treated as an increasing function of frequency: more common means more important, less common means more likely noise.

**Step 2 — state retrieval's implicit value function, from the same paper.** Retrieval's $P_{init}(e)$ uses a *mean*, specifically to avoid rewarding high-frequency mention (Critique C's own quote: "the mean-not-sum... refuses to reward repetition"), and the type-layer formula applies $1/\log(\deg(t)+1)$ — a term that actively *penalizes* high degree, which correlates directly with high frequency of mention. Both retrieval-side mechanisms treat "more common" as evidence *against* importance, or at least not evidence for it.

**Step 3 — show the two value functions are not just different, but contradictory on the same underlying quantity.** Frequency is the mechanism construction uses to promote something into the graph, and something structurally similar (degree, which correlates with mention frequency) is what retrieval actively suppresses once inside the graph. A candidate schema with frequency exactly at the promotion boundary is, by construction's logic, borderline-valuable; by retrieval's logic, a fact instantiating that schema would be actively discounted for the same property that got it promoted.

**Step 4 — show the asymmetric damage this causes.** Because construction runs first and is irreversible (a fact never promoted never enters the graph), retrieval's opposite value function never gets a chance to act on what construction excluded — the rare, valuable schema that construction's frequency threshold cut is never available for retrieval's rarity-rewarding IDF term to boost. The system's two halves would, given the chance, reward opposite things — but only one half ever gets to decide what the other half sees.

## Practical pattern

Apply "preserve, then decide" as a design review checklist for any pipeline with an early, irreversible filtering stage:

1. audit every construction-time or ingestion-time filter for irreversibility — if content removed at this stage can never be recovered by any later stage, that filter needs to be held to a much higher bar of certainty than a stage whose decisions can be revisited;
2. check whether different stages of your own pipeline implicitly disagree about what "valuable" means (as frequency-based promotion and rarity-rewarding retrieval do here) — if they do, whichever stage runs first and is irreversible silently wins the disagreement, regardless of which value function is actually more correct;
3. default to annotation over deletion for anything resembling a conflict, contradiction, or edge case — a "conflicts-with" edge with both provenances costs almost nothing to store and preserves optionality a resolved, deleted-loser record does not;
4. when a step in your pipeline "must" resolve ambiguity (there is only one output slot, as in the Joe example), treat that constraint itself as a design smell worth revisiting — could the schema instead carry multiple candidate values with confidence scores, deferred to query time?

## Common traps

- building a multi-stage pipeline where different stages embed contradictory assumptions about what "important" or "valuable" means, without ever checking for the contradiction because each stage was designed and tested independently;
- treating early-stage filtering as low-risk because "we can always improve it later," when the actual damage (irreversibly discarded content) already happened and cannot be recovered by any later improvement;
- resolving an ambiguous or contested fact into a single confident-looking output because the data structure only has room for one, rather than questioning whether the data structure should have room for more;
- conflating "the system produced an answer" with "the system produced a grounded answer" — an LLM resolution agent forced to pick one of two irreconcilable facts is not becoming more grounded by picking, it is substituting its own prior for missing evidence while looking exactly as confident as when it had real evidence.

## Takeaways

- MemGraphRAG's own retrieval-time formulas (mean not sum, logarithmic hub damping) implicitly reward rarity — while its construction-time promotion rule implicitly punishes it — and because construction runs first and is irreversible, the contradiction always resolves in construction's favor, silently.
- The general principle — preserve information and defer judgment to the moment with the most context, rather than committing early when context is scarcest — applies far beyond GraphRAG, to any pipeline stage that discards information it cannot get back.
- Concretely: before shipping any construction-time or ingestion-time filter, ask whether its removal is reversible — if not, hold it to the standard of "would I regret this if I later understood the removed content's true value," not merely "does this look like noise right now."
