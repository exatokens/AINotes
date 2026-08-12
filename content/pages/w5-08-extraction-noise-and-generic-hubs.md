---
id: w5-08-extraction-noise-and-generic-hubs
title: "Who Extracts: The Scooby-Doo Problem and Generic-Entity Hubs"
week: 5
topic: "Act II: The Web of Knowledge — Triplets, Types, and Three Layers"
order: 8
summary: LLM extraction is cheap but indiscriminate, and the generic entities it inflates — United States, Person, Protein — become exactly the hubs Act I predicted, now with a name.
---

Knowledge graphs are old ambitions with a new labor force. In the pre-LLM era they were built by subject-matter experts sitting with passages and hand-crafting triplets — effort that scaled with man-hours, which is why only governments, Google, and pharma could afford serious ones. Then language models arrived, very good at exactly language: ask for triplets and triplets pour out. What looked like a million man-years suddenly seemed achievable on the GPU under your desk.

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
