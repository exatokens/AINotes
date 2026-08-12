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
