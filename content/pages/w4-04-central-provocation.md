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

- Query against the claim it actually means: $\cos(q, e_2) = \dfrac{q \cdot e_2}{\|q\|\,\|e_2\|} = \dfrac{1}{1 \times 1} = 1$ — a perfect match.
- Query against the whole paragraph: $\cos(q, e_{para}) = \dfrac{q \cdot e_{para}}{\|q\|\,\|e_{para}\|} = \dfrac{1/3}{1 \times \sqrt{1/3}} \approx \dfrac{0.333}{0.577} \approx 0.577$

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
