---
id: w2-10-bi-cross-encoder-sphere
title: "Bi-Encoders, Cross-Encoders, and the Unit Sphere"
week: 2
topic: "Act III: The Geometry of Belief"
order: 10
summary: There are exactly two ways to ask a BERT-like model how related two texts are, and the trade between them organizes the architecture of every retrieval system; both rely on cosine similarity, which is a dot product in disguise once vectors are normalized onto the unit sphere.
---

## Two ways to use a BERT

There are exactly two ways to ask a BERT-like model "how related are these two pieces of text," and the difference between them organises the entire architecture of a retrieval system.

In the **bi-encoder**, you push each text through the model separately, pool each into a single vector (the previous page's mean-pooling), and compare the two vectors by cosine. The query never meets the document inside the model — they meet only at the very end, as two points whose angle you measure.

In the **cross-encoder**, you concatenate the query and the document and push them through the model together, so every word of the query can attend to every word of the document at every layer; the model emits a single relevance score.

| | Bi-encoder | Cross-encoder |
|---|---|---|
| When comparison happens | after encoding, as two frozen vectors | during encoding, via full cross-attention |
| Accuracy | good, sometimes blunt | far more accurate — catches subtleties frozen vectors miss |
| Cost at scale | encode each document once, in advance; query time is a nearest-neighbour lookup | must re-run the full model for every query–document pair |
| Slogan | encodes once, compares forever | compares once, must re-encode every time |

The trade is stark and it's all about *when* the comparison happens. The cross-encoder is ruinously expensive at scale: finding the best of a million documents means running the full model a million times per query, because the score can't be computed until the query is in hand. The bi-encoder is the opposite: every document is embedded once and stored in Qdrant; at query time you embed only the query and let geometry find its neighbours in milliseconds.

> A serious RAG system uses both, in a cascade. The bi-encoder casts a wide, cheap net, retrieving perhaps the top hundred candidates from millions by pure geometry. Then the cross-encoder — the expensive, accurate judge — re-ranks just those hundred. Wide and cheap, then narrow and sharp.

## Cosine, dot product, and the sphere

A load-bearing clarification about measuring nearness, because three quantities are easy to confuse. The dot product $\langle u,v\rangle$ measures alignment, but it's contaminated by length — a long vector scores high against everything, simply for being long. The **cosine similarity** removes the contamination by dividing out both lengths,

$$\cos\theta = \frac{\langle u,v\rangle}{\lVert u\rVert \lVert v\rVert}$$

leaving a pure measure of direction: $+1$ perfectly aligned, $0$ orthogonal, $-1$ opposed — exactly what we want when meaning lives in which way a vector points, not how long it is. Once every vector sits on the **unit sphere** ($\lVert u\rVert=\lVert v\rVert=1$), the cosine *is* the dot product, and it's also a monotonic function of the Euclidean distance between the two points. On the sphere, the three notions of nearness collapse into one — which is why a vector database can rank by a plain dot product on normalised vectors and you can speak of "cosine similarity" and "nearest neighbour" interchangeably.

```python
# why normalization matters: dot product rewards length, cosine does not
def dot(u, v):
    return sum(a*b for a, b in zip(u, v))

def norm(u):
    return dot(u, u) ** 0.5

def cosine(u, v):
    return dot(u, v) / (norm(u) * norm(v))

query = [1.0, 0.0]
short_match = [0.9, 0.1]     # highly aligned, modest length
long_offtopic = [2.0, 1.8]   # less aligned, but long

print("dot product:", dot(query, short_match), "vs", dot(query, long_offtopic))
print("cosine:     ", round(cosine(query, short_match), 3), "vs", round(cosine(query, long_offtopic), 3))
# the long, less-aligned vector can win on raw dot product alone — a classic retrieval bug
```

> **The practical trap:** forget to normalise, and dot-product search silently rewards long vectors — a handful of high-norm chunks then dominate every result list. Many a mysterious retrieval bug is a missing normalisation. On the sphere, length is meaningless by construction, and the bug cannot occur.
