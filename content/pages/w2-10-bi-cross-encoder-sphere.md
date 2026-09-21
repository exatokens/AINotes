---
id: w2-10-bi-cross-encoder-sphere
title: "Bi-Encoders, Cross-Encoders, and the Unit Sphere"
week: 2
topic: "Act III: The Geometry of Belief"
order: 10
summary: There are exactly two ways to ask a BERT-like model how related two texts are, and the trade between them organizes the architecture of every retrieval system; both rely on cosine similarity, which is a dot product in disguise once vectors are normalized onto the unit sphere.
---

## Core intuition

A model can compare two texts either before or after they meet. The difference between these choices is the difference between a fast retrieval system and a slow but precise re-ranker.

## Why it matters

Bi-encoders are built for scale; cross-encoders are built for precision. The entire retrieval stack exists to exploit that trade-off deliberately.

## Instructor framing

This chapter converts the bi-encoder from Week 1 into a deliberate architectural choice rather than the only option. Once students see that a cross-encoder exists and is more accurate, the natural question is "why doesn't everyone just use that?" — and the answer (cost) is what motivates the entire cascade architecture the rest of the course builds toward: cheap-and-wide, then expensive-and-narrow.

## Worked example

Imagine searching a million legal documents for "clauses that void a warranty if the product is modified." A cross-encoder could, in principle, read the query alongside each of the million documents and render a careful, context-sensitive verdict for each — but that means running a full transformer forward pass a million times for a single question, which at realistic latency would take longer than a human paralegal. A bi-encoder instead has already read and embedded all one million documents in advance, once, overnight; at query time it embeds only the question and does a geometric lookup that returns candidates in milliseconds. The bi-encoder is not smarter — it is just asking a cheaper question ("which points are nearby?") instead of the harder one ("which document, read carefully against this exact question, actually supports it?").

This is the architecture of modern search. The question is not which model is better in the abstract, but when the comparison should happen, and at what cost.

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






## Math explained step by step

Walk through exactly why normalisation is not optional, using the code example above.

**Step 1 — the raw dot product conflates two different things.** $\langle u,v \rangle = \sum_i u_i v_i$ grows both when the vectors point the *same way* and when either vector is simply *longer*. A vector database that ranks by raw dot product cannot tell these two causes apart.

**Step 2 — see the failure concretely.** `short_match = [0.9, 0.1]` is nearly perfectly aligned with the query `[1.0, 0.0]` but has modest length. `long_offtopic = [2.0, 1.8]` points in a noticeably different direction but is long enough that its raw dot product with the query, $2.0$, beats `short_match`'s $0.9$. A ranking by raw dot product would rank the *less relevant* document first, purely because some upstream process (a longer chunk, an unnormalised model) happened to give it a bigger vector.

**Step 3 — dividing out both lengths repairs this.** $\cos\theta = \langle u,v\rangle / (\lVert u \rVert \lVert v \rVert)$ rescales both vectors to length one before comparing, so only direction survives. Recomputing: `short_match` now scores $\approx 0.994$, `long_offtopic` scores $\approx 0.727$ — the correct ranking is restored.

**Step 4 — see why "cosine" and "dot product" become interchangeable in practice.** If you normalise every vector to unit length *once*, at indexing time, before storing it, then the plain dot product at query time already *is* the cosine similarity — no per-query division required. This is exactly why production vector databases normalise embeddings on ingestion: it turns an expensive-looking division into free arithmetic.

## Practical pattern

When you build or audit a retrieval stack, use this as a checklist:

1. confirm your vector database's distance metric matches how your embeddings were produced — if the embedding model was trained and evaluated using cosine similarity, configure the index to use cosine (or normalise vectors and use dot product), not raw Euclidean distance;
2. normalise embeddings to unit length at ingestion time rather than at query time — it is cheaper to do once per document than to divide on every comparison;
3. reserve the cross-encoder for a small shortlist (typically 20-200 candidates) surfaced by the bi-encoder — never run it over a full corpus, and never skip it entirely if your task has subtle relevance judgments (negation, exceptions, precise numeric thresholds) that a single cosine score tends to blur;
4. if search results seem to favor unusually long chunks or documents for no clear semantic reason, check normalisation first — it is one of the most common, and most silent, retrieval bugs.

## Common traps

- storing unnormalised embeddings and querying with raw dot product or Euclidean distance, then wondering why longer chunks systematically outrank shorter, more relevant ones;
- running a cross-encoder over the entire corpus "to be safe," which turns a millisecond search into a multi-minute one at real corpus sizes;
- assuming a bi-encoder's top result is trustworthy on its own for high-stakes decisions, when a cross-encoder re-rank of even the top 20-50 candidates would catch subtle mismatches the bi-encoder's frozen vectors cannot see;
- mixing embeddings from two different models (or two different normalisation conventions) in the same index and comparing them directly — cosine similarity is only meaningful when both vectors were produced compatibly.

## Takeaways

- A bi-encoder compares texts after encoding them separately (fast, scalable); a cross-encoder compares them together with full cross-attention (slow, precise).
- Production systems use both in a cascade: bi-encoder for wide cheap recall, cross-encoder for narrow precise re-ranking.
- Cosine similarity is a dot product on vectors normalised to the unit sphere — normalise once at ingestion, and every later query-time comparison is both cheaper and correct.
- If your retrieval is silently biased toward longer documents, check normalisation before you touch the model.
