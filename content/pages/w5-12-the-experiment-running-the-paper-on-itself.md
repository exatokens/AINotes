---
id: w5-12-the-experiment-running-the-paper-on-itself
title: "The Experiment: Running the Paper on Itself"
week: 5
topic: "Act III: The Many Meanings of GraphRAG"
order: 12
summary: Running MemGraphRAG's own construction pipeline on a dozen passages of the paper itself produced a staircase of thresholds where no rung admits signal without noise.
---

To see how the construction phase behaves on real text, the paper itself was taken as the corpus — a dozen good passages from it — and its own pipeline was run on them: an afternoon with an LLM extracting fact and schema triplets, exactly as prescribed. Twelve passages yielded **38 fact triplets and 27 distinct schemas**; the schema frequency table was built exactly as the paper prescribes, and the counting began.

## Core intuition

The architecture's own construction rules can be tested on the paper itself. If the graph-building logic is sound, it should preserve the meaningful signal and reject the noise without becoming a caricature of the corpus.

## Why it matters

The self-experiment is a sanity check for the entire pipeline. It exposes whether frequency-based filtering is really selecting meaning or merely eliminating the long tail.

## Instructor framing

This page models good scientific practice: rather than critique MemGraphRAG's promotion rule abstractly, the course tests it directly on the paper's own text and lets the numbers speak. Emphasize to students that running a paper's own method on itself is a genuinely underused sanity check — it costs an afternoon and one LLM, and it caught a failure mode that would otherwise require trusting the paper's own benchmark tables at face value.

## Worked example



Twelve real passages, one real LLM extraction pass, and a real frequency count — no synthetic example needed here, because the paper's own text supplied one. The champion schema at frequency five turned out to be the least interesting claim in the entire paper ("a method uses a technique" — true of nearly every methods paper ever written); the schema encoding the paper's actual central contribution (the process-causes-deficiency diagnosis) sat three rows down, at frequency three; and the paper's own three-agent architecture — the very thing being described — tied at frequency one with an unrelated copyright notice. If a construction rule cannot tell its own paper's thesis apart from its own paper's legal boilerplate using nothing but frequency, that is not a corner case — it is the rule failing on the exact document that motivated writing it.

This is the crucial empirical test: if the graph-building mechanism cannot distinguish the paper's important concepts from boilerplate, the construction rule is not model-based enough to be trusted.

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






## Math explained step by step

Walk the staircase table's numbers through, one threshold at a time, to see exactly why no rung wins.

**Step 1 — $\tau=4$: verify the graph is technically valid but practically useless.** One schema (frequency 5) survives, contributing five "X uses Y" facts. Each of these facts is an isolated edge — no two share a connected entity in the toy example — so the resulting graph is five disconnected fragments, not a graph anyone could traverse meaningfully. This is structural fragmentation, one of MemGraphRAG's own named diseases, produced *by* its own cure.

**Step 2 — $\tau=3$: see the best-looking result, and why it's still incomplete.** The diagnosis schema (frequency 3) now survives alongside the banality. This looks like progress — real content is admitted — but the paper's own architectural description (the three agents, each frequency 1) is still entirely absent. A user asking "how does this paper's own system work" would get nothing back, even though that information exists in the source passages.

**Step 3 — $\tau=1$: see the necessary trade to recover the missing content.** Lowering the threshold all the way to admit the three agents (the paper's methodology) necessarily also admits the copyright notice, because both sit at exactly the same frequency. There is no value of $\tau$ strictly between 1 and 3 that could separate them — they are tied.

**Step 4 — generalize the conclusion beyond this toy corpus.** This isn't a quirk of these particular twelve passages. Any frequency-based threshold partitions candidates into exactly two bins: "frequency $\geq \tau$" and "frequency $< \tau$." Whenever a genuinely important claim and a genuinely unimportant one happen to share a frequency (which, on a Zipfian-distributed corpus, happens constantly in the long tail), no single value of $\tau$ can place them in different bins — the threshold is a one-dimensional cut applied to information that needs at least a second dimension (some notion of intrinsic importance, independent of count) to separate correctly.

## Practical pattern

Take this experiment as a template for auditing any frequency-, popularity-, or count-based filtering step in your own pipeline:

1. before trusting a novel construction or filtering rule at scale, run it on a small, deeply-understood sample first — ideally a document whose ground-truth important content you can enumerate by hand, the way this experiment used the paper's own known thesis and architecture as ground truth;
2. explicitly check the threshold's behavior at its most permissive setting (here, $\tau=1$) for what else gets admitted alongside the content you actually want — if noise and signal are tied at that setting, the filter cannot separate them at any setting;
3. if you find a tie between valuable and non-valuable content at the same frequency (as here), that is a signal to add an orthogonal filtering dimension (source type, explicit review, structural position in the document) rather than searching for a better single threshold value — no threshold value fixes a problem that isn't one-dimensional;
4. document and communicate this kind of finding even when it doesn't change the aggregate benchmark number — the paper's own pilot study found frequency filtering "slightly improves accuracy" on average, and this experiment does not contradict that; it shows the average can hide a specific, predictable, and consequential failure on exactly the content (rare, valuable, technical claims) that matters most in specialist domains.

## Common traps

- trusting a construction or filtering rule's aggregate benchmark performance without separately checking its behavior on the specific content type (rare, important, technical claims) most likely to be harmed;
- assuming a small-scale sanity-check experiment like this one is not "real evidence" because it isn't a full benchmark run — a twelve-passage, ground-truth-known experiment can reveal a structural failure mode that a thousand-document benchmark's averages would hide;
- searching for a better threshold value when the actual problem is that the threshold, as a one-dimensional cut, structurally cannot separate the two things you need separated;
- generalizing "frequency-based filtering works" from one benchmark's average result to all corpora, without checking whether that benchmark's data was Zipfian and long-tailed the way most real technical and specialist corpora are.

## Takeaways

- Running a graph-construction rule on the paper's own text is a cheap, powerful sanity check — it surfaced a failure (tying the paper's own methodology with a copyright notice) that no amount of reading the paper's benchmark tables would have shown.
- No single frequency threshold can separate "rare and important" from "rare and noise," because a one-dimensional cut cannot resolve a distinction that requires a second, non-frequency signal.
- Concretely: before trusting any frequency- or popularity-based filter in your own pipeline, test it on a small sample with known ground truth — if valuable and worthless content tie at the same frequency there, no threshold tuning will fix it, and you need an orthogonal signal instead.
