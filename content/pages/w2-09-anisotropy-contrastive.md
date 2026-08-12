---
id: w2-09-anisotropy-contrastive
title: "Anisotropy and Its Cure: Triplet Loss and InfoNCE"
week: 2
topic: "Act III: The Geometry of Belief"
order: 9
summary: A model trained only to predict words learns a representation crammed into a narrow cone, because attraction with no repulsion has one stable end state — contrastive learning supplies the missing repulsive force, and its modern form, InfoNCE, is the softmax and negative log-likelihood again, now sculpting the globe itself.
---

## When attraction is not enough

Last week we glimpsed a flaw in raw embeddings and named its cure in passing. Now we face it squarely. When a model is trained only to predict words — only the masked-word game, only negative log-likelihood — it learns a representation that is powerful but geometrically lopsided. All the vectors drift into a narrow cone, crammed into one corner of the globe, so that even two unrelated sentences look fairly similar because everything looks fairly similar. This pathology is **anisotropy** — the space is not the same in all directions — and it's poison for retrieval, which lives or dies on the gaps between things.

> The deep cause: the language-modelling loss is almost entirely a force of *attraction*. It pulls words that share contexts together, but it's never explicitly told to push anything apart. A field of forces with attraction and no repulsion has one stable end state: a single huddled clump. Stars need gas pressure to resist gravity; embeddings need repulsion to resist collapse.

## The shape of the contrastive objective

What's missing is a repulsive force, and this is precisely what **contrastive learning** supplies. Show the model pairs that should be close (a sentence and its paraphrase) and pull them together; also show it pairs that should be far (a sentence and an unrelated one) and push them apart. Attraction and repulsion, together, do what gravity alone never could: they spread the representations out to fill the sphere, restoring **isotropy**.

The oldest form is **triplet loss**. Take an anchor $a$, a positive $p$ that should be close (a paraphrase), and a negative $n$ that should be far (unrelated). Ask that the anchor sit nearer its positive than its negative by at least a margin $m$:

$$L_{\text{triplet}} = \max\big(0,\ \lVert a-p\rVert^2 - \lVert a-n\rVert^2 + m\big)$$

Read it as etiquette enforced by a small fine: if the positive is already closer than the negative by the margin, the loss is zero — no gradient. Only when a negative crowds too close, or a positive drifts too far, does the loss switch on and pull the positive in while shoving the negative away. The margin $m$ is what stops the trivial solution of squashing everything to a point, where all distances vanish.

Plug in real numbers to watch the switch flip. Let the anchor be $a=(1.0,0.2)$, its paraphrase $p=(0.9,0.1)$ sitting close by, and a margin $m=0.2$. Against a genuinely unrelated negative $n=(-0.8,0.1)$, the squared distances are $\lVert a-p\rVert^2=(0.1)^2+(0.1)^2=0.02$ and $\lVert a-n\rVert^2=(1.8)^2+(0.1)^2=3.25$. The loss is $\max(0,\ 0.02-3.25+0.2)=\max(0,-3.03)=0$ — the positive is already comfortably nearer, so no gradient fires and this triplet is left alone. Now let a harder negative crowd in at $n'=(0.85,0.15)$, almost on top of the anchor: $\lVert a-n'\rVert^2=(0.15)^2+(0.05)^2=0.025$, so the loss becomes $\max(0,\ 0.02-0.025+0.2)=\max(0,0.195)=0.195$ — strictly positive. Same formula, same margin; the only thing that changed was how close the impostor dared to get, and that's precisely when the gradient switches on and starts pulling $p$ in and shoving $n'$ away.

The modern, more powerful form is **InfoNCE**. Instead of one negative, gather a whole batch of them, and ask the model to pick the true positive out of the crowd — a classification problem, scored, inevitably, by a softmax over similarities:

$$L_{\text{InfoNCE}} = -\log \frac{\exp(\text{sim}(a,p)/\tau)}{\sum_j \exp(\text{sim}(a,x_j)/\tau)}$$

Look at what this is: a softmax over the similarity of the anchor to every candidate, scored by negative log-likelihood of placing the mass on the true positive — the entire opening act of the day, in one line: softmax in the denominator, $-\log$ out front, a temperature $\tau$ on the scores, now turned to the task of spreading a space rather than classifying a picture.

```python
# a toy InfoNCE loss: one anchor, one true positive, three negatives
import math

def sim(u, v):
    return sum(a*b for a, b in zip(u, v))  # dot product as similarity

anchor = [1.0, 0.2]
positive = [0.9, 0.1]                 # a true paraphrase, close to the anchor
negatives = [[-0.8, 0.1], [0.1, 0.9], [-0.2, -0.9]]  # unrelated sentences
tau = 0.2

candidates = [positive] + negatives
scores = [math.exp(sim(anchor, c) / tau) for c in candidates]
loss = -math.log(scores[0] / sum(scores))
print("InfoNCE loss:", round(loss, 3))
```

The quality of the lesson depends entirely on the quality of the negatives. **Easy negatives** — a physics sentence against an obviously unrelated history sentence — teach almost nothing, since the model already knows they're far apart, so the gradient is near zero. The instructive negatives are the **hard** ones: documents that look deceptively similar to the right answer but are subtly wrong — the near-duplicate clause from the wrong contract, the regulation from the wrong jurisdiction. Mining these, often by using the model itself to find its own most embarrassing confusions and feeding them back as negatives, is where most of the real gain in a fine-tuned retriever comes from. A cheap trick that helps for free is **in-batch negatives**: within a training batch, every other example's positive serves as a negative for yours, giving a batch of size $B$ a free $B-1$ negatives — exactly why contrastive training loves large batches.

## Seeing the repulsion

Claims about geometry should be seen, not believed. Embed the same corpus of physics, biology, and history sentences three ways — a raw language model (attraction only), a generic off-the-shelf sentence embedder (contrastively trained on broad data), and a model contrastively fine-tuned on this specific dataset. For each, compute two collections of cosine similarities: **within-class** (physics-to-physics) and **between-class** (physics-to-history). Plot each as a histogram.

In a good embedding space, the within-class histogram sits high, the between-class histogram sits low, and — the number to watch — the two barely overlap. In the raw, anisotropic embedder, the two histograms sit almost on top of one another, both bunched near high similarity: everything looks alike, signal drowned. Moving from generic to domain-tuned, the between-class histogram slides left, the overlap shrinking before your eyes. A single number to put on a slide: the overlap area of the two histograms, or a silhouette score — it falls as the space gets healthier. This is what "a good embedding" means, made quantitative, and it's exactly the property your retriever silently exploits every time it works.
