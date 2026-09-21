---
id: w2-09-anisotropy-contrastive
title: "Anisotropy and Its Cure: Triplet Loss and InfoNCE"
week: 2
topic: "Act III: The Geometry of Belief"
order: 9
summary: A model trained only to predict words learns a representation crammed into a narrow cone, because attraction with no repulsion has one stable end state — contrastive learning supplies the missing repulsive force, and its modern form, InfoNCE, is the softmax and negative log-likelihood again, now sculpting the globe itself.
---

## Core intuition

Raw language modelling builds attraction but not repulsion, so all sentences drift toward the same region of space. Contrastive learning adds the missing force: bring true neighbors together and push wrong neighbors apart until the representation spreads out into a meaningful geometry.

## Why it matters

Retrieval lives in the gaps between vectors. If everything collapses into a dense cone, the model cannot distinguish related from unrelated text. The cure is not more training alone — it is a training objective that actively shapes the metric structure of the embedding space.

## Instructor framing

This chapter closes the loop opened in Week 1's anisotropy demonstration. There, we only *observed* that raw contextual embeddings crowd into a cone. Here, we get the mechanism — why a model trained only to predict words inevitably ends up there — and the fix. Teach it as cause and effect: no repulsive force in the loss, therefore no repulsion in the geometry, therefore a training objective must supply the missing force deliberately.

## Worked example

Picture training a model only ever rewarded for saying "yes, these two words appeared near each other" — never once told "and these two did not." Every gradient step nudges some pair of vectors closer together, and no gradient step ever pushes any pair apart. Repeat that for a few hundred billion tokens and the entire vocabulary drifts toward a single crowded region, the way a room full of people told only "step toward someone you recognize" will eventually huddle into one corner, never having been told "and leave space around strangers." Contrastive learning is the instruction to leave space: for every pair pulled together, another pair is explicitly pushed apart, and the room fills out.

This is the first major geometry fix in the book. The problem is not just model quality; it is the shape of the latent space. Anisotropy is an architectural failure of the representation itself.

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






## Math explained step by step

Follow the triplet-loss numbers from above one more time, but narrate the *why* at each move.

**Step 1 — measure how far apart the anchor is from a good match and a bad one.** $\lVert a-p\rVert^2$ and $\lVert a-n\rVert^2$ are just squared distances — no cleverness yet, only bookkeeping of where three points currently sit.

**Step 2 — compare them, and add a safety margin $m$.** The quantity $\lVert a-p\rVert^2 - \lVert a-n\rVert^2 + m$ is negative when the positive is already comfortably closer than the negative *by more than the margin* — meaning the current arrangement is already good enough, and there is nothing to fix.

**Step 3 — clip at zero with $\max(0, \cdot)$.** Why clip instead of letting the loss go negative? Because a negative loss would mean the optimiser keeps pulling the positive even closer forever, chasing a reward that should have already been satisfied. Clipping says: once the ordering is safely correct, stop pushing — save the gradient for pairs that still need it.

**Step 4 — see what "the gradient switches on" means physically.** When a hard negative crowds close enough that the clipped quantity is positive, gradient descent does two things at once: it pulls the anchor and positive together (shrinking $\lVert a-p\rVert^2$) and pushes the anchor and negative apart (growing $\lVert a-n\rVert^2$). This is the literal repulsive force that raw language-modelling loss never applied — encoded as two opposite-signed updates to two different distances.

**Step 5 — InfoNCE is the same idea, generalized to many negatives at once via softmax.** Instead of one negative and a margin, InfoNCE treats "pick the true positive out of a whole batch of candidates" as a classification problem, scored by the same negative-log-likelihood machinery from earlier this week. More negatives per step means more repulsive comparisons per gradient update, which is why contrastive training is hungry for large batches or mined hard negatives — both are ways of buying more "push" per step.

## Practical pattern

When you are choosing or fine-tuning an embedding model for retrieval, the actionable checklist is:

1. never deploy a raw language-model encoder (one only pretrained with masked-word prediction) directly for retrieval — check its release notes for a contrastive fine-tuning stage before trusting cosine similarity as a ranking signal;
2. if fine-tuning your own retriever, invest in *hard negative mining* before adding more data — a batch of easy negatives contributes almost no gradient, and most of the real quality gain comes from the near-miss negatives;
3. use in-batch negatives by default (every other example's positive is a free negative for yours) and increase batch size if you can afford it — it is one of the cheapest levers on retrieval quality;
4. periodically audit the deployed model's anisotropy directly (average cosine of random unrelated pairs from your own corpus, as in Week 1) rather than trusting a benchmark leaderboard number from someone else's data distribution.

## Common traps

- deploying a model fine-tuned only for classification or generation as a retrieval embedder, assuming any transformer's final-layer vectors are retrieval-ready — without a contrastive objective, they are not;
- training a contrastive retriever on only easy negatives (random unrelated documents), then being confused when it fails on the subtle real-world confusions — the wrong-jurisdiction regulation, the near-duplicate clause — that easy negatives never taught it to separate;
- using a small batch size for contrastive fine-tuning and wondering why quality plateaus, without realizing in-batch negative count scales with batch size;
- reading "improved embedding quality" claims from a vendor without checking whether they measured within-class vs. between-class separation on data resembling yours, rather than on a generic benchmark.

## Takeaways

- Anisotropy is not a mysterious flaw — it is the predictable result of a loss function built entirely from attraction with no repulsion.
- Contrastive learning (triplet loss, InfoNCE) fixes this by explicitly rewarding separation between unrelated pairs, not just closeness between related ones.
- Hard negatives, not easy ones, are where most of the real training signal lives — mine them deliberately.
- Before trusting an embedding model's cosine similarity scores in production, verify it was contrastively fine-tuned, not just pretrained on raw text.
