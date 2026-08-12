---
id: w5-03-erdos-renyi-vs-barabasi-albert
title: "Two Kinds of Randomness: Erdős–Rényi versus Barabási"
week: 5
topic: "Act I: The Mathematics of the City"
order: 3
summary: Fair-coin random graphs have no hubs; real networks do, because they grow by preferential attachment — and every knowledge graph inherits the same heavy tail.
---

Recall from the last page: **degree** $k$ is just the number of edges touching a vertex, and the **degree distribution** $P(k)$ is the fraction of vertices in the whole graph that have exactly $k$ of them — the census of the city, what fraction of houses sit on quiet lanes of degree two versus boulevards of degree two hundred. This page asks: what shape should $P(k)$ have, and does that shape ever produce a hub — a vertex with wildly more connections than everyone else?

What should a "random" network look like? The first honest answer came from Erdős and Rényi: take $n$ vertices, and flip a coin for every possible pair, adding the edge with probability $p$. Degree is then a sum of independent coin flips, and for large $n$ its distribution is Poisson:

$$P(k) = e^{-\langle k \rangle} \frac{\langle k \rangle^k}{k!}$$

Read it as: the chance a vertex has exactly $k$ edges, given that the *average* vertex has $\langle k \rangle$ edges. Plug in a small number to see it bite. Suppose the average degree is $\langle k \rangle = 4$ (everyone knows about four others). The chance of landing exactly on the average, $P(4) = e^{-4} \cdot 4^4/4! = e^{-4} \cdot 256/24 \approx 0.195$ — about one vertex in five. Now ask for a vertex with ten times the average, degree 40: $P(40) = e^{-4} \cdot 4^{40}/40!$, a number with about seventeen zeros after the decimal point. Not rare — *effectively impossible*. That is the Poisson tail: it dies factorially, faster than any exponential. In an Erdős–Rényi world, everyone is middle class. There are no hubs.

Then, in 1999, Barabási and Albert measured real networks — the web, citation graphs, metabolic networks — and found something entirely different: the degree distribution follows a **power law**,

$$P(k) \propto k^{-\gamma}, \qquad \gamma \approx 2\text{–}3$$

Read the symbols one at a time. "$\propto$" means "is proportional to" — $P(k)$ is some constant times $k^{-\gamma}$, so what matters is the shape, not the exact scale. $\gamma$ (gamma) is a positive number, the **exponent**, usually somewhere between 2 and 3 for real-world networks; it controls how fast the probability falls off as $k$ grows. And the whole expression says: as degree $k$ goes up, probability goes down — but *slowly*, as a negative power of $k$, not as a factorial.

Plug in real numbers to feel the difference from Poisson. Take $\gamma = 2$, so $P(k) \propto k^{-2} = 1/k^2$. A vertex with degree $k=1$ gets a relative weight of $1/1^2 = 1$. A vertex with degree $k=100$ — a hundred times more connected — gets $1/100^2 = 1/10{,}000$. So the hub is ten thousand times rarer than the ordinary vertex — rare, yes, but nowhere near the Poisson case above, where a vertex ten times the average was off the scale of measurement entirely. That is the whole content of "heavy tail": the probability of a hub is small, but it is only *polynomially* small, not *factorially* small — and in a graph with millions of vertices, "one in ten thousand" is not a curiosity, it is a guaranteed handful of hubs. Plot it log–log and the signature is unmistakable: a straight line, where Poisson would plummet like a cliff.

| | Erdős–Rényi | Barabási–Albert (real networks) |
|---|---|---|
| Wiring rule | fair coin flip on every pair | new vertices link preferentially to well-connected ones |
| Degree distribution | Poisson, tight bump | power law, heavy tail |
| Hubs | essentially impossible | expected, and load-bearing |
| Log–log plot | downward parabola | ruler-straight line |

## Why reality disobeys the fair coin

Real networks are not wired by fair coins. They grow, and they grow by **preferential attachment**: a new vertex does not link uniformly at random — it links preferentially to vertices already well connected. A new webpage links to Wikipedia, not a random page; a new paper cites the famous paper; a newcomer gravitates to the person everyone is already talking to. The rich get richer (the Matthew effect), and the mathematics of rich-get-richer growth provably yields the power law. Hubs are not anomalies; they are what growth plus preference manufactures, always.

```python
# preferential attachment, toy version -- new nodes prefer high-degree targets
import random

degree = {0: 1, 1: 1}   # start with one edge, 0-1
edges = [(0, 1)]

for new_node in range(2, 300):
    # probability of attaching to an existing node is proportional to its degree
    targets, weights = zip(*degree.items())
    chosen = random.choices(targets, weights=weights, k=1)[0]
    edges.append((new_node, chosen))
    degree[new_node] = degree.get(new_node, 0) + 1
    degree[chosen] += 1

top_hubs = sorted(degree.items(), key=lambda kv: -kv[1])[:5]
print(top_hubs)  # a handful of early nodes accumulate wildly disproportionate degree
```

Hold two consequences, one for each half of the afternoon. First: **hubs make networks navigable** — they are the airports through which short routes pass, which is exactly what makes the small-world phenomenon (next page) possible at all. Second: **hubs make networks noisy to expand around** — touch a hub and you touch everything it touches, most of which has nothing to do with you. When we meet the oldest, naivest meaning of "GraphRAG" this afternoon — expand the query through graph neighbors — that second consequence explains, in one line, why the naive approach degrades exactly when the graph gets interesting.

> **The one thing to remember.** Real networks are heavy-tailed, not Poisson. Hubs are a mathematical certainty of growth-by-preference, not noise — and a knowledge graph extracted from a corpus is a real network, so it will have them too.
