---
id: a5-03-centrality-smart-keyword-extraction
title: "Centrality: Why Structure Beats Frequency"
week: 5
topic: "Act II: Knowledge Graphs as an Agent's Domain Memory"
order: 3
summary: A keyword extractor that ranks by how central a term is in a domain's knowledge graph, rather than by raw frequency, surfaces the terms that actually matter to a domain — frequency is only a tiebreaker.
course: ai_agents
---

Ask an agent to pull the "important" keywords out of a piece of text and you'll usually get a word cloud — big font for whatever repeats most. It's a reasonable first guess, and it's also frequently wrong in exactly the way that matters: the most-repeated word in an article is often a connective or a topic label, not the concept doing the real intellectual work. A smarter extractor needs a notion of importance that isn't just "shows up a lot."

The traditional answer to this — TF-IDF, evolving into BM25 — is a real improvement over raw counting, because it discounts words that are common everywhere and rewards words that are distinctive to this particular document relative to a larger corpus. But it's still fundamentally a statistical trick about word distributions, not a model of what the domain actually knows to be important. The course's answer is to go one level deeper: build a knowledge graph of the domain, and let the graph's own structure tell you which terms matter.

The printer-repairman story is the cleanest possible illustration of why structural position, not surface frequency, is the right signal for importance — and it's worth sitting with before diving into the mechanics.

## Core intuition

Centrality measures, borrowed from graph theory, quantify how structurally important a node is within a network — not how often it's mentioned, but how much the network's connectivity depends on it. A high-centrality node is one that many other important things connect through; remove it, and the graph fractures or loses coherence.

Applied to a domain's knowledge graph — a curated set of triplets like `<Fremont, is part of, California>` — the keyword extractor's job becomes: take the text, find which of its terms correspond to nodes in the domain graph, and rank them by centrality rather than by how many times they appear in this one document. Frequency only breaks ties among terms with comparable centrality.

## Why it matters

The corporate anecdote makes the abstraction concrete: executives at a large organization discovered, via social-network analysis of internal communication, that the most central node in their organization's trust network wasn't a senior executive — it was the printer repair man, the one person who moved through every department and talked to everyone. He wasn't the most frequently mentioned employee in any single conversation, but he was structurally load-bearing: remove him, and the informal channels connecting departments would fracture. When leadership needed to communicate a new company direction, they used him as the transmission point, precisely because of his structural centrality, not his job title or how often his name came up in any given meeting.

The same logic makes a knowledge-graph-based keyword extractor meaningfully better than a frequency-based one: a term with high eigenvector centrality — one that bridges many other important concepts in the domain — is doing real conceptual work in that domain, whether or not this particular article happens to mention it five times or just once.

## Instructor framing

Anchor this page on the printer-repairman story before touching any graph math — it's the single fastest way to get students to feel, intuitively, the difference between "mentioned a lot" and "structurally important," and that intuition is what makes the subsequent formalism (eigenvector centrality, degree centrality) land as a precise version of something they already believe, rather than an arbitrary formula.

## Worked example

Suppose you're building a keyword extractor for a satellite-engineering newsletter. A raw frequency count on a given issue might surface "satellite," "launch," and "team" as the top three terms — all true, all present, none of them useful for a glossary, because they're generic to the whole domain and don't help a reader who already knows they're reading about satellites.

Now overlay the domain's knowledge graph: nodes like `orbital decay`, `attitude control`, `thermal vacuum testing`, connected by edges to a dense web of related concepts (propulsion, telemetry, radiation hardening). Even if "attitude control" appears only twice in this particular article, its position in the graph — bridging propulsion concepts to telemetry concepts to failure-mode concepts — gives it high centrality. The extractor surfaces it as a high-value term precisely because of that bridging role, not its local repetition count, and a reader unfamiliar with the domain genuinely benefits from having it defined, in a way they would not benefit from having "satellite" defined.

## Math explained step by step

Formalize eigenvector centrality, since it's the specific measure the course points to and it has a clean recursive definition worth deriving rather than quoting.

**Step 1 — state the recursive idea.** A node's importance should be proportional to the importance of the nodes it's connected to — being connected to one highly important node should count for more than being connected to ten unimportant ones. If $x_i$ is the centrality score of node $i$, and $A_{ij} = 1$ if nodes $i$ and $j$ are connected (0 otherwise), the recursive definition is

$$x_i = \frac{1}{\lambda}\sum_{j} A_{ij}\, x_j$$

for some constant $\lambda$.

**Step 2 — recognize the eigenvector equation.** Written for the whole vector $\mathbf{x}$ at once, this is $\lambda \mathbf{x} = A\mathbf{x}$ — exactly the definition of an eigenvector of the adjacency matrix $A$ with eigenvalue $\lambda$. The centrality scores that make this self-consistent (each node's importance defined in terms of its neighbors' importance) are the components of the dominant eigenvector of $A$ — the one associated with the largest eigenvalue, which guarantees all-positive, comparable scores under standard graph conditions.

**Step 3 — see why this beats frequency for the newsletter case.** A term's raw count in one document is a purely local, single-document statistic; eigenvector centrality is a property of the term's position in the entire domain graph, built from potentially thousands of documents. "Attitude control" can score low on step 3's local count in this article and still score high on the global eigenvector calculation, because its high score is earned from the *domain's* overall structure, not from anything in the specific text being processed today.

**Step 4 — use frequency correctly, as the tiebreaker it is.** Among terms with comparable centrality — genuinely ambiguous ties — local frequency in the current document is a reasonable secondary signal for which of the tied terms is most relevant *to this specific piece*. This is the intended, narrow role for frequency: it resolves ties among already-important terms, it doesn't define importance on its own.

## Practical pattern

Building a centrality-based keyword extractor for a real domain:

1. build or acquire a knowledge graph for the domain — modern practice is to have an LLM read a large batch of domain documents and generate the triplets in one pass, which the course notes can produce over 10,000 nodes in minutes from a hundred documents, rather than the years of manual curation earlier knowledge-graph efforts required;
2. do a light human curation pass — a single day of review is often enough to strip out low-value, noisy triplets the LLM surfaced, and the graph is still highly useful even without exhaustive cleanup;
3. compute a centrality measure (eigenvector centrality is the course's default) over the whole graph once, offline — this doesn't need to be recomputed per document, because the domain graph moves slowly even as new articles arrive;
4. for a given piece of text, extract the subset of terms that match graph nodes, rank by precomputed centrality, and use local frequency only to break near-ties;
5. re-run the graph build periodically (not per document) to absorb genuinely new domain concepts, since a slow-moving core with occasional additions is the expected shape of the graph over time.

## Common traps

- computing centrality per-document instead of over the whole domain graph, which throws away the entire benefit — a single article's internal link structure is far too sparse to distinguish structurally important terms from incidental ones;
- letting frequency dominate the ranking again by weighting it too heavily relative to centrality, quietly reverting to a word-cloud extractor with extra steps;
- treating the LLM-generated knowledge graph as needing to be perfect before it's useful — waiting for exhaustive human curation delays deployment for a marginal quality gain, when a one-day noise-removal pass captures most of the value;
- assuming the domain graph needs to be rebuilt every time new content arrives — the course is explicit that high-centrality, foundational concepts are stable over long periods, and treating the graph as needing constant full rebuilds wastes compute for little benefit.

## Takeaways

- Frequency measures how much a term repeats in one document; centrality measures how structurally load-bearing a term is across the entire domain — they answer different questions, and only centrality answers "is this actually important to the domain."
- Eigenvector centrality formalizes "important because connected to important things" as the dominant eigenvector of the graph's adjacency matrix — a recursive definition with a precise linear-algebra solution.
- Build the domain knowledge graph once (LLM-generated, lightly curated), compute centrality over the whole graph, and use per-document frequency only as a tiebreaker among already-central terms.
