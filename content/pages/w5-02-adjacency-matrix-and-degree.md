---
id: w5-02-adjacency-matrix-and-degree
title: "The Adjacency Matrix: Where a Graph Becomes Calculable"
week: 5
topic: "Act I: The Mathematics of the City"
order: 2
summary: Numbering the vertices and recording edges as a matrix turns a drawing into something you can compute with — degree, walk counts, and every algorithm that follows.
---

A picture of dots and lines is for humans; a matrix is for mathematics. Number the vertices $1$ through $n$ and define the adjacency matrix $A$ by

$$A_{ij} = \begin{cases} 1 & \text{if there is an edge between } i \text{ and } j \\ 0 & \text{otherwise} \end{cases}$$

## Core intuition

A graph is not just a drawing in a notebook. It becomes computationally useful only when we encode the structure in a matrix and let linear algebra do the work.

The adjacency matrix is the formal spreadsheet of the graph: every edge is a 1, every non-edge is a 0, and every algorithm then becomes a matrix computation over the same object.

## Why it matters

The graph's semantics live in the pattern of edges; the matrix lets us reason about counts, connectivity, and propagation in ways a human eye cannot see directly.

## Instructor framing

Run the "room is a graph" exercise before showing any formula — students who have just counted their own degree by hand, and watched one person turn out to be a hub, will recognize $k_i = \sum_j A_{ij}$ as a description of something they just did, not a new abstraction to memorize. The matrix should feel like notation for an experience, not the other way around.

## Worked example



This is the move from picture to algorithm. Once the graph is encoded as a matrix, connectivity is no longer a diagram — it is arithmetic.

For an undirected graph, $A$ is symmetric. If edges carry weights — and in knowledge graphs they will, counting how often two things co-occur — the ones become weights instead. This single object converts a graph from a drawing into something you can compute with: powers of $A$ count walks. The entry $(A^2)_{ij}$ counts the two-step paths from $i$ to $j$; $(A^k)_{ij}$ counts the $k$-step walks. Every graph algorithm you meet today — community detection, PageRank, spectral analysis — is, underneath its costume, linear algebra performed on $A$ or on matrices derived from it.

## Degree: the first vital statistic

The row sums of $A$ give the degree of vertex $i$:

$$k_i = \sum_j A_{ij}$$

the number of edges touching it. A vertex of high degree is a **hub**; a vertex of degree one is a leaf, a cul-de-sac of the city. Degree is local and almost embarrassingly simple — and the *statistics* of degree across a large graph turn out to be one of the deepest fingerprints a network has (the subject of the next page).

```python
# a tiny knowledge graph as an adjacency matrix -- entities as rows/cols
entities = ["Einstein", "Germany", "Nobel Prize", "Relativity"]
idx = {e: i for i, e in enumerate(entities)}

A = [[0]*4 for _ in range(4)]
for u, v in [("Einstein","Germany"), ("Einstein","Nobel Prize"), ("Einstein","Relativity")]:
    A[idx[u]][idx[v]] = A[idx[v]][idx[u]] = 1   # undirected, symmetric

degree = [sum(row) for row in A]
for e, k in zip(entities, degree):
    print(f"{e:12s} degree={k}")
# Einstein degree=3 -- already a small hub; the others are leaves, degree=1
```

## The room is a graph: an exercise before the mathematics

Before plotting any distribution, become one. Everyone stand. You are the vertices. Draw an edge to every person in the room you had spoken to — before today — for at least five minutes. Count your edges on your fingers: that number is your degree. Tally the room: how many people have degree one or two? Five? Ten? And — there is always one — who is carrying degree twenty-plus, connected to half the cohort?

What you just produced is a **degree distribution** — the function $P(k)$ giving the fraction of vertices with degree $k$: the census of the city, how many houses sit on quiet lanes versus boulevards. Notice its shape: not a bell curve. Most people hold a few edges; one or two hold a wild number. That asymmetry — most vertices poor, a few absurdly rich — is not an accident of the room. It is close to a law of nature for real networks, which the next page formalizes.

> **The one thing to remember.** The adjacency matrix is not bookkeeping scenery — it *is* the machine. Community detection, PageRank, and spectral clustering are all linear algebra performed on $A$ or on matrices built from it. Everything that follows today is this matrix wearing different costumes.






## Math explained step by step

Unpack why $A^k$ counts $k$-step walks — this is the single fact that makes the adjacency matrix "the machine," not just a storage format.

**Step 1 — see what one matrix multiplication actually computes.** $(A^2)_{ij} = \sum_m A_{im} A_{mj}$: for every intermediate vertex $m$, multiply "is there an edge $i \to m$?" by "is there an edge $m \to j$?" — the product is $1$ only if *both* edges exist, i.e., only if $m$ is a valid stepping-stone on a two-step path from $i$ to $j$.

**Step 2 — see why summing over $m$ counts paths, not just checks existence.** Summing $A_{im}A_{mj}$ over every possible intermediate vertex $m$ adds up one for each valid stepping-stone — so $(A^2)_{ij}$ is literally the *count* of distinct two-step walks from $i$ to $j$, not merely a yes/no flag for "is a two-step walk possible."

**Step 3 — verify this on the Einstein example.** With `Einstein` connected to `Germany`, `Nobel Prize`, and `Relativity` (degree 3, all leaves otherwise), $(A^2)_{\text{Germany}, \text{Nobel Prize}}$ would be $1$: the only two-step walk from Germany to Nobel Prize goes Germany → Einstein → Nobel Prize, passing through the one shared hub. This is already a primitive form of multi-hop reasoning — computing which entities are connected *through* an intermediary, without ever re-reading the source text.

**Step 4 — generalize to why every later algorithm reduces to this.** PageRank repeatedly multiplies a vector by (a normalized version of) $A$ to find which vertices accumulate the most "walk traffic" over many steps. Spectral clustering examines $A$'s eigenvectors to find groups of vertices that are internally well-connected. Community detection (next pages) compares actual edge density to what $A$'s degree sequence would predict by chance. None of these are separate machines — they are different questions asked of the same matrix, which is exactly the claim "everything today is this matrix wearing different costumes."

## Practical pattern

When you extract a knowledge graph and represent it computationally:

1. store edges with weights from the start (co-occurrence counts, confidence scores from extraction) rather than plain 0/1 — nearly every downstream algorithm (PageRank, community detection) is more informative on a weighted graph, and retrofitting weights later is harder than including them at construction;
2. compute and inspect the degree distribution immediately after extraction, before running any retrieval on top of the graph — a small number of extraction bugs (a mis-linked entity, an overly generic node like "the company") often show up as implausible degree spikes;
3. use sparse matrix representations for real corpora — a knowledge graph adjacency matrix over even a modest corpus is enormous and overwhelmingly zero, and a dense matrix implementation will not scale;
4. treat $A^2$, $A^3$, etc. as your first diagnostic tool for multi-hop questions ("what connects to what, through what") before reaching for a more complex graph algorithm — often the two- or three-step walk count already answers the question.

## Common traps

- storing a knowledge graph's edges as unweighted 0/1 when the extraction process actually produced confidence scores or co-occurrence counts — this discards real signal before any algorithm gets to use it;
- treating high degree as automatically meaning "important" without checking whether it's a genuine hub (a real conceptual center) or an extraction artifact (an overly generic entity like "data" or "system" that spuriously links to everything);
- using dense matrix operations on a large real-world knowledge graph, then being surprised by memory or performance problems that sparse representations would have avoided entirely;
- skipping the degree-distribution sanity check after extraction, and only discovering an extraction bug much later when a downstream retrieval or clustering result looks obviously wrong.

## Takeaways

- The adjacency matrix converts a graph from a picture into a computable object — every later graph algorithm (PageRank, community detection, spectral clustering) is linear algebra performed on $A$ or a matrix derived from it.
- Matrix powers $A^k$ count $k$-step walks, giving a direct, cheap way to answer "what connects to what, through what" without touching the original text.
- Concretely: compute and inspect the degree distribution of any extracted knowledge graph before building retrieval on top of it — an implausible hub is usually an extraction bug, not a genuine discovery.
