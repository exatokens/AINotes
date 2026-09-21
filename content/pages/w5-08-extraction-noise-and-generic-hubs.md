---
id: w5-08-extraction-noise-and-generic-hubs
title: "Who Extracts: The Scooby-Doo Problem and Generic-Entity Hubs"
week: 5
topic: "Act II: The Web of Knowledge — Triplets, Types, and Three Layers"
order: 8
summary: LLM extraction is cheap but indiscriminate, and the generic entities it inflates — United States, Person, Protein — become exactly the hubs Act I predicted, now with a name.
---

Knowledge graphs are old ambitions with a new labor force. In the pre-LLM era they were built by subject-matter experts sitting with passages and hand-crafting triplets — effort that scaled with man-hours, which is why only governments, Google, and pharma could afford serious ones. Then language models arrived, very good at exactly language: ask for triplets and triplets pour out. What looked like a million man-years suddenly seemed achievable on the GPU under your desk.

## Core intuition

LLM extraction is fast but noisy. It creates a graph that is easier to build than to trust, because every accidental textual pattern becomes a candidate edge.

This is the price of cheap extraction: more graph coverage, and more semantic junk.

## Why it matters

The extracted graph is not a pure reflection of the corpus. It is a mixture of real knowledge, boilerplate, annotation noise, and generic background concepts. Once that noisy graph is used for retrieval, the graph's own hubs and communities can amplify the bad edges.

## Instructor framing

The "Scooby-Doo" anecdote is memorable on purpose — use it as the standing joke for the rest of the course whenever a student proposes a graph technique without addressing extraction noise. The deeper point worth surfacing explicitly: this page is Act I's mathematics (heavy tails, preferential attachment) returning as a *diagnosis* of a real engineering problem, not a new topic — students should recognize this as the pattern the whole course repeats, theory first, then the theory explaining a mess you can actually see.

## Worked example



This is the operational disease of extracted graphs: they are not just incomplete, they are contaminated with false positives and generic hubs. The methods we learn later are all attempts to clean or dampen that contamination.

But play the comparison game: what is the difference between an SME extracting triplets and a language model doing it? The SME knows the context — the result is domain-bounded, distilled, curated. The machine transcribes whatever the text happens to say, and corpora say all sorts of things. Somewhere in a margin sits an annotation — "pending Scooby-Doo's review" — and now $\langle \text{document}, \text{pending-review-by}, \text{Scooby-Doo} \rangle$ is a fact in your knowledge graph, filed diligently next to the physics, right alongside copyright notices and tracked-changes debris. The graph became cheap and simultaneously became noisy — and the entire research lineage toured this afternoon, from Microsoft GraphRAG's frequency-weighted edges to MemGraphRAG's promotion thresholds, is a series of attempts to answer the noise question an SME's salary used to answer.

## Hubs return: the generic-entity problem

Cash in the first of the morning's IOUs. A knowledge graph extracted from a large corpus is a real-world network, so everything from Act I applies verbatim: heavy-tailed degree distribution, small-world structure, communities within communities, two-to-four levels of meaningful hierarchy. And in a knowledge graph, we can say precisely who the hubs are: the **generic entities**. *United States. Microsoft. Protein. Person.* The things connected to everything, because every second passage mentions them. Preferential attachment guarantees their existence; extraction noise inflates them further.

Hubs are double-edged, exactly as promised in Act I. They make the knowledge city navigable — multi-hop paths between distant concepts route through them, the way flights route through Frankfurt. And they are semantic traps for any naive process that spreads outward along edges: expand two hops from "USA" and you have retrieved the encyclopedia.

```python
# a toy extraction pass: noisy LLM-style triplets from one passage,
# with a generic entity accumulating disproportionate degree
extracted = [
    ("Einstein", "born-in", "Germany"),
    ("Einstein", "cited-in", "Physics Review"),
    ("Marie Curie", "cited-in", "Physics Review"),
    ("Bohr", "cited-in", "Physics Review"),
    ("this-document", "pending-review-by", "Scooby-Doo"),   # extraction noise
    ("this-document", "licensed-under", "CC-BY"),            # boilerplate, not physics
]

degree = {}
for u, _, v in extracted:
    degree[u] = degree.get(u, 0) + 1
    degree[v] = degree.get(v, 0) + 1

hubs = sorted(degree.items(), key=lambda kv: -kv[1])
print(hubs)
# "Physics Review" is already the hub -- touch it and you touch every cited author,
# exactly the pattern that will doom naive neighbor expansion this afternoon
```

Every serious system this afternoon carries a scar shaped like this paragraph — you will recognize it when MemGraphRAG mutes its type-layer hubs with a logarithmic damper it politely calls **hub suppression**, and when community-detection approaches rely on modularity's $k_i k_j / 2m$ term, which is precisely a correction for expected hub-degree.

> **The one thing to remember.** The mathematics of Act I is not scenery; it is scar tissue. Generic-entity hubs are a mathematical certainty of any large extracted graph, and every GraphRAG variant this afternoon is judged partly by how it copes with them.






## Math explained step by step

Connect extraction noise directly to the Barabási-Albert mathematics from Act I, step by step.

**Step 1 — recall that preferential attachment guarantees hubs in any real, growing network.** A knowledge graph extracted from a corpus grows one document at a time, and any entity mentioned disproportionately often (a country, a common noun like "protein," a ubiquitous organization) accumulates edges faster simply because it appears more — the same rich-get-richer mechanism from the previous pages, now with named culprits.

**Step 2 — see why LLM extraction accelerates this beyond what careful curation would produce.** An SME extracting triplets by hand implicitly filters: they recognize "pending Scooby-Doo's review" as a stray annotation, not a fact, because they understand context and relevance. An LLM extraction pass run uniformly over every chunk has no such filter unless explicitly prompted for one — every grammatically valid head-relation-tail pattern in the text becomes a candidate edge, including boilerplate, margin notes, and copyright text. This inflates the denominator of "how many spurious edges attach to generic entities" well beyond what preferential attachment alone would predict.

**Step 3 — quantify the downstream cost using the degree-driven expansion cost from two pages ago.** If neighbor expansion from vertex $v$ touches roughly $k_v$ neighbors, and a generic hub like "Physics Review" or "United States" has $k_v$ orders of magnitude larger than a specific entity's degree, then any two-hop expansion that happens to pass through that hub returns a candidate set dominated by the hub's other neighbors — most of which share nothing with the original query except an accidental co-mention.

**Step 4 — see why the fix has to happen at multiple stages, not just once.** Modularity's $k_i k_j / 2m$ term (Act I) already discounts expected hub connectivity when detecting communities — so community-based GraphRAG partially self-corrects. But neighbor-expansion-style GraphRAG (next page) has no such correction unless one is added explicitly, which is exactly why later systems add hub suppression, frequency weighting, or promotion thresholds as separate, deliberate engineering responses to a problem Act I's mathematics predicted would exist before any of these systems were built.

## Practical pattern

Building extraction robustness into a knowledge-graph pipeline:

1. add an explicit filtering pass after extraction that flags and removes boilerplate patterns (copyright notices, "pending review," licensing text, document metadata) before they enter the graph — this is a cheap, high-value step that an SME would have done implicitly and an LLM extraction pass will not do unless asked;
2. compute the degree distribution of the extracted graph and manually inspect the top 20-50 highest-degree entities — in a domain-bounded corpus, an unexpectedly generic top entity (a country, a common noun) is almost always an extraction artifact worth suppressing or type-filtering rather than a genuine finding;
3. apply frequency-aware weighting or damping to generic entities before running any expansion or diffusion algorithm on the graph — treat "United States" and "Compound X's specific side effect" as needing fundamentally different treatment in any traversal, not the same weight per edge;
4. budget for iteration — extraction noise is not a one-time cleanup, since a corpus that grows will continue to inflate existing hubs and introduce new ones, so periodic re-auditing of the degree distribution should be part of the pipeline's maintenance, not a one-off launch task.

## Common traps

- running LLM triplet extraction with no post-processing filter and trusting the resulting graph as-is, only discovering boilerplate and annotation noise once retrieval quality is already visibly degraded;
- treating a high-degree entity as automatically meaningful ("United States must be important, look how connected it is") rather than checking whether the degree reflects genuine centrality or just ubiquity;
- applying neighbor expansion (next page) on a freshly-extracted graph without any hub suppression, then being surprised when a two-hop walk from any entity of interest floods the result with unrelated content;
- underestimating how much of the "cost" difference between naive extraction and curated extraction is precisely this filtering work — cheap extraction did not eliminate the SME's labor, it deferred it to a cleanup and dampening stage that must still be built.

## Takeaways

- Generic-entity hubs in an extracted knowledge graph are not a bug specific to any one extraction run — they are a mathematical certainty of preferential attachment, worsened by LLM extraction's lack of implicit contextual filtering.
- The entire later research lineage (frequency weighting, hub suppression, promotion thresholds) exists specifically to answer the noise problem this page names, so understanding the problem here makes every later fix legible as a response rather than an arbitrary design choice.
- Concretely: after any LLM-based triplet extraction, inspect the top 20-50 highest-degree entities by hand before trusting the graph — an unexpectedly generic entity at the top is almost always extraction noise, not a genuine discovery.
