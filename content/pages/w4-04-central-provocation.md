---
id: w4-04-central-provocation
title: "The Central Provocation and the Geometry of Dilution"
week: 4
topic: "Act I: The Purpose Problem"
order: 4
summary: The design principle for the rest of the week, plus the geometric reason it is necessary — a multi-claim paragraph embeds near the average of its claims, which dilutes its similarity to any one pointed query.
---

Here is the design principle that the rest of the week obeys.

> Do not wait for the user's query to match your documents. Manufacture documents that match your user's queries.

## Core intuition

A query is usually a focused fact, while a raw document chunk is often a mixture of many facts. Retrieval becomes harder when the chunk is a muddy average of several meanings instead of a crisp retrieval target.

## Why it matters

The central problem of all retrieval systems is geometric mismatch: the query points at one fact, but the chunk centroid sits somewhere between several facts. The solution is to create narrower evidence units that can match the query directly.

## Instructor framing

This page is the mathematical spine of the entire week — everything downstream (factoids, QA pairs, RAPTOR) is a different engineering response to the same one inequality. Make sure students can state $\cos(q, e_{para}) \le \cos(q, e_k)$ in plain words before moving on: "a query aimed at one fact scores lower against a paragraph containing that fact than against the fact alone, because the paragraph's other content drags the average down." Everything else this week is commentary on that sentence.

## Worked example



This chapter is the heart of the week. The problem is not that the model is bad; it is that the indexing unit is too broad for the user's intent. The fix is to manufacture documents that are query-shaped rather than prose-shaped.

If that feels like cheating, good — the best engineering often does. We are not gaming the retriever; we are aligning it. And there is a precise, geometric reason we must.

## Why dilution happens

Picture mixing five different paint colors on one palette. You do not get any of the five back — you get a muddy grey that resembles each of them only faintly. Averaging blurs. A paragraph that asserts $n$ distinct claims does the same thing to its embedding: rather than landing near any one claim, it lands near their muddy average.

Formally, to a first approximation the paragraph's embedding behaves like the average of its constituent meanings,

$$e_{para} \approx \frac{1}{n}\sum_{i=1}^{n} e_i,$$

where each $e_i$ is the embedding of one self-contained claim and $n$ is how many claims the paragraph makes — this is just "add up the $n$ claim-vectors and divide by $n$," the ordinary arithmetic mean, applied to vectors instead of numbers. A pointed query $q$ — "what is the population of Berlin?" — sits near one vertex $e_k$, the one claim it actually cares about. Its similarity to the paragraph is then a diluted quantity,

$$\cos(q, e_{para}) \approx \frac{1}{n}\sum_{i=1}^{n} \cos(q, e_i) \le \cos(q, e_k),$$

because the one term that matters, $\cos(q, e_k)$, is averaged down by $n-1$ irrelevant neighbours sitting in the same paragraph.

**A worked example you can check by hand.** Suppose a paragraph makes exactly three claims, and — to keep the arithmetic simple — imagine each claim's embedding points along its own axis in a toy 3-dimensional space, so the three claims are mutually at right angles (completely unrelated to one another, which is what "three distinct claims" means geometrically):

$$e_1 = [1, 0, 0], \qquad e_2 = [0, 1, 0], \qquad e_3 = [0, 0, 1]$$

The paragraph's embedding is their average, $e_{para} = \frac{1}{3}(e_1+e_2+e_3) = \left[\frac{1}{3}, \frac{1}{3}, \frac{1}{3}\right]$.

Now send in a pointed query aimed squarely at claim 2 — say $q = [0, 1, 0]$, identical to $e_2$. Compare the two similarities:

- Query against the claim it actually means: $\cos(q, e_2) = \d\frac{q \cdot e_2}{\|q\|\,\|e_2\|} = \d\frac{1}{1 \times 1} = 1$ — a perfect match.
- Query against the whole paragraph: $\cos(q, e_{para}) = \d\frac{q \cdot e_{para}}{\|q\|\,\|e_{para}\|} = \d\frac{1/3}{1 \times \sqrt{1/3}} \approx \d\frac{0.333}{0.577} \approx 0.577$

Even though the query is a dead-on match for claim 2, indexing the paragraph as one averaged vector caps the similarity at about $0.577$ instead of $1$. The other two claims, sitting in the average, are dragging the score down by roughly 40% — that is the dilution the inequality predicts, with real numbers behind it.

Treat this as a heuristic, not a theorem — real pooling is nonlinear, and real claims are never perfectly orthogonal — but the direction is exactly right, and it is the same shrinkage the Centroid Tug-of-War later makes you feel with your own feet.

Here is the same idea in code, at a more realistic scale (five claims, sixty-four dimensions, random rather than hand-picked):

```python
# a toy demonstration of embedding dilution
import numpy as np

def cos(a, b):
    return a @ b / (np.linalg.norm(a) * np.linalg.norm(b))

rng = np.random.default_rng(0)
# five roughly-orthogonal "claim" vectors in a toy space
claims = rng.normal(size=(5, 64))
claims /= np.linalg.norm(claims, axis=1, keepdims=True)

# the paragraph that asserts all five claims embeds near their centroid
e_para = claims.mean(axis=0)

# a pointed query aimed squarely at claim 2
q = claims[2] + 0.05 * rng.normal(size=64)

print("query vs. paragraph  :", cos(q, e_para))   # diluted
print("query vs. claim 2    :", cos(q, claims[2]))  # undiluted, always higher
```

Factoid extraction is the antidote: index $e_k$ on its own, and the dilution disappears. Act II builds exactly that artifact.

> **Key reference.** Proposition-level indexing is formalized in Chen et al., "Dense X Retrieval: What Retrieval Granularity Should We Use?" Their FactoidWiki corpus yields about 2.25 propositions per sentence on average — a measure of how much meaning ordinary prose compresses, and how many retrieval targets passage-level indexing hides.






## Math explained step by step

Recap the derivation above as four moves, with the "why" made explicit at each.

**Step 1 — model a multi-claim paragraph's embedding as an average.** $e_{para} \approx \frac{1}{n}\sum_i e_i$ is not an arbitrary assumption; it follows from mean-pooling (Week 2) — the encoder produces one vector per token, and pooling averages them, so a paragraph mixing $n$ distinct claims produces a vector that behaves like the average of what each claim alone would have produced.

**Step 2 — apply the same averaging to the similarity score, since cosine is (approximately) linear in this sense.** $\cos(q, e_{para}) \approx \frac{1}{n}\sum_i \cos(q, e_i)$ — the paragraph's similarity to the query is approximately the *average* of the query's similarity to each individual claim, not the similarity to the one claim that actually matters.

**Step 3 — isolate why this average is always at most the best individual term.** Averaging $n$ numbers, one of which is the largest (the true match, $\cos(q,e_k)$) and $n-1$ of which are smaller (unrelated claims), always produces a result $\le$ the largest term alone — this is just the definition of an average, applied to similarity scores instead of exam grades.

**Step 4 — the worked numbers show the size of the effect, not just its direction.** The hand-computed example loses about 40% of the possible similarity ($1 \to 0.577$) to only two irrelevant neighbouring claims; the code example shows the same shrinkage at a more realistic scale (five claims, 64 dimensions). The practical lesson is that dilution is not a rounding error — it is often large enough, by itself, to push a genuinely relevant paragraph below the top-$k$ cutoff.

## Practical pattern

Apply the dilution inequality as a diagnostic and a design rule:

1. when a query aimed at one specific fact fails to retrieve a chunk you know contains that fact, suspect dilution before suspecting the embedding model — check how many distinct claims share that chunk;
2. for corpora with dense, multi-claim paragraphs (reference material, encyclopedic text, dense technical writing), budget for factoid-level extraction rather than relying on chunk-level embeddings alone;
3. use the dilution formula as a rough sizing tool: a chunk asserting $n$ roughly-orthogonal claims loses on the order of $(n-1)/n$ of its potential similarity to a query aimed at any one of them — for $n=5$, that is up to 80% of the possible score, which is often the difference between top-1 and outside top-10.

## Common traps

- diagnosing a missed retrieval as an embedding-model failure when it is actually a dilution failure — the fact was present in the corpus, but buried inside a multi-claim chunk;
- assuming smaller chunks always fix dilution — a small chunk with only one claim helps, but Week 3's lexical-cohesion and bridging-inference pathologies show that smaller chunks can introduce *new* problems if cut carelessly;
- treating the dilution formula as an exact law rather than a first-order approximation — real pooling is nonlinear and real claims are rarely perfectly orthogonal, so use it for intuition and rough sizing, not as a precise prediction;
- over-correcting by extracting factoids so aggressively that context needed to interpret the factoid (Week 3's endophora and lexical cohesion) is lost in the process.

## Takeaways

- A multi-claim chunk's embedding behaves like the average of its claims, and averaging mathematically caps its similarity to any single-claim query below what a dedicated single-claim vector would achieve.
- The size of this dilution grows with the number of unrelated claims sharing one chunk — it is often large enough to push a relevant fact out of the top-k entirely.
- Concretely: when a known-relevant fact fails to surface in retrieval, first count how many distinct claims share its chunk before tuning the embedding model or reranker.
