---
id: w2-02-surprise-entropy-crossentropy
title: "Surprise, Negative Log-Likelihood, and the Cross-Entropy Family"
week: 2
topic: "Act I: The Shape of a Decision"
order: 2
summary: Surprise is a decreasing function of the probability you assigned to what actually happened, and the logarithm is the repair that sends certainty to zero surprise — from there, entropy, cross-entropy, and perplexity are just this one quantity, averaged and re-dressed.
---

A belief is worthless until the world tests it, and the test has a feeling attached: surprise. Suppose you believed, 99% confident, that it would rain — and it rained. Barely a flicker. Now suppose you judged rain a 1% long shot — and it poured. You're astonished. Surprise is a **decreasing function of the probability you assigned to the thing that actually happened.**

The mathematics of surprise is the grammar of learning. Every time a model is wrong, the loss is not vague; it is the exact amount of surprise caused by the misjudgement.

## Core intuition

Surprise measures how badly the world violated your expectations. A very likely event causes little surprise when it occurs. A very unlikely event causes massive surprise when it occurs.

The logarithm is the right math for this because it turns a probability scale into a stable, additive measure of information.

## Why it matters

This chapter underlies model training. The objective used to train language models is built from surprise: the model is punished more heavily when it assigns a tiny probability to the correct outcome.

That is why the negative log-likelihood is so central to ML. It directly measures how badly the model was surprised by the data.

## Instructor framing

This chapter gives the probabilistic core of learning. The course is telling you that training is not magic; it is a process of minimizing expected surprise until the model assigns high probability to the data it actually sees.

## Worked example


If a model assigns probability 0.1 to the token that actually appears, the surprise is $-\log_2(0.1) \approx 3.32$ bits. That is a dramatic failure. If it assigns 0.9, the surprise is only 0.15 bits.

The loss is therefore dominated by confident errors, which is exactly what we want from a learning rule.

## Why the logarithm is forced

The simplest function that decreases as $p$ grows and blows up as $p\to 0$ is the inverse, $1/p$. It's a good guess — a 1% rain that ruins the picnic gives surprise 100. But it has a fatal flaw: at $p=1$, the event you were sure of, $1/p = 1$, not zero. The floor is in the wrong place; the inverse's range is $[1,\infty)$ when we need $[0,\infty)$.

The repair is the logarithm. Define surprise as

$$S(p) = \log\frac{1}{p} = -\log p$$

Check the ends: at $p=1$, $\log 1 = 0$ — certainty fulfilled costs nothing. As $p\to 0$, $-\log p \to +\infty$ — the impossible, made real, is infinitely surprising. This single quantity, $-\log p$, is the atom of information theory; in base two it is measured in **bits**, and it answers "how many yes/no questions, on average, would I have needed to pin this outcome down?"

## From one surprise to many: negative log-likelihood

A model faces not one event but a whole corpus. Because surprise is a logarithm, total surprise over many independent events is simply their sum:

$$S_{\text{total}} = \sum_k -\log p_k = -\sum_k \log p_k$$

This is the **negative log-likelihood (NLL)** — the accumulated surprise of a model across all the evidence it was asked to predict. Averaged rather than summed, it's what falls, epoch by epoch, on every training dashboard. A model learning is, literally, a model becoming less surprised by the world.

Make it concrete. On five successive missing-word predictions, suppose your model placed probabilities $0.5, 0.9, 0.1, 0.8, 0.6$ on the words that actually turned out correct:

| prediction $p$ | surprise $-\log_2 p$ (bits) |
|---|---|
| 0.5 | 1.00 |
| 0.9 | 0.15 |
| 0.1 | 3.32 |
| 0.8 | 0.32 |
| 0.6 | 0.74 |

Sum: 5.53 bits total; average: 1.11 bits per word. The third event — a 10% long shot that happened anyway — contributes more than the other four combined. This is the signature of the NLL, and it's a feature, not a bug: the loss is dominated by cases where the model was **confidently wrong**, so the gradient shouts loudest exactly where the model most needs to change its mind.

```python
# negative log-likelihood, entropy-style bookkeeping, on five predictions
import math

probs = [0.5, 0.9, 0.1, 0.8, 0.6]   # probability placed on the word that actually occurred
surprises = [-math.log2(p) for p in probs]
total = sum(surprises)
avg = total / len(surprises)
perplexity = 2 ** avg
print("per-event bits:", [round(s, 2) for s in surprises])
print("total bits:", round(total, 2), "avg bits:", round(avg, 2), "perplexity:", round(perplexity, 2))
```

## Entropy, cross-entropy, perplexity

Three words deserve pinning down, because they are all this morning's surprise, averaged and re-dressed.

If the world truly draws outcomes from a distribution $p$, the average surprise a perfectly calibrated observer would feel is the **entropy**:

$$H(p) = -\sum_i p_i \log p_i = \mathbb{E}_p[-\log p]$$

A fair coin has entropy of one bit — one unavoidable yes/no question per flip. A two-headed coin has entropy zero. Entropy is the irreducible floor of surprise, unavoidable even with perfect beliefs.

But you hold some model $q$, not the truth $p$. How surprised are you, on average, when the world draws from $p$ but you scored it with $q$? That's the **cross-entropy**:

$$H(p,q) = -\sum_i p_i \log q_i$$

which is, term for term, the average NLL we just built — the two names are interchangeable. Minimising cross-entropy means making your beliefs $q$ as unsurprised as possible by the truth $p$; it bottoms out exactly when $q=p$.

Take the average surprise in bits and raise two to its power: that's the **perplexity**,

$$\text{PPL} = 2^{H}$$

the effective number of equally-likely options you're choosing among. A model with average surprise of three bits is as confused as someone guessing uniformly among $2^3=8$ possibilities. A player spreading chips evenly over ten candidate words scores $\log_2 10 \approx 3.32$ bits — perplexity ten, the whole vocabulary, no narrowing at all. A fluent player scores near zero bits — perplexity near one, effectively certain.

> **Entropy** is the surprise you'd feel with correct beliefs; **cross-entropy** is the surprise you actually feel with your beliefs. The gap between them — always non-negative, zero only when you're exactly right — is the **Kullback–Leibler divergence**. It measures the distance between distributions on a curved surface, and we'll meet it again when we get to search as motion on a globe.



## Math explained step by step

Derive the KL divergence mentioned above from the entropy and cross-entropy already built, so "the gap between them" is shown, not just asserted.

**Step 1 — write both quantities side by side.** Entropy is $H(p) = -\sum_i p_i \log p_i$; cross-entropy is $H(p,q) = -\sum_i p_i \log q_i$. Both are averages over the *true* distribution $p$ — the only difference is which distribution sits inside the logarithm.

**Step 2 — subtract them.** $H(p,q) - H(p) = -\sum_i p_i \log q_i - \left(-\sum_i p_i \log p_i\right) = \sum_i p_i \log\frac{p_i}{q_i}$. This is, by definition, the **Kullback–Leibler divergence** $D_{KL}(p\|q)$ — the average, under the truth, of the log-ratio between what's true and what you believe.

**Step 3 — see why it can never be negative.** By concavity of $\log$, Jensen's inequality gives $\sum_i p_i \log\frac{q_i}{p_i} \le \log\sum_i p_i \cdot \frac{q_i}{p_i} = \log\sum_i q_i \le \log 1 = 0$. Flipping the sign, $D_{KL}(p\|q) = -\sum_i p_i\log\frac{q_i}{p_i} \ge 0$ — with equality exactly when $q_i=p_i$ for every $i$ (the log-ratio is zero everywhere).

**Step 4 — read off the consequence for training.** Since $H(p,q) = H(p) + D_{KL}(p\|q)$ and $H(p)$ doesn't depend on the model at all (it's a fixed property of the data), minimising cross-entropy $H(p,q)$ over $q$ is *identical* to minimising $D_{KL}(p\|q)$ — training is, exactly and not just metaphorically, the act of pulling the model's distribution toward the true one, and cross-entropy sits at its theoretical minimum, $H(p)$, only once $q=p$.

**Step 5 — connect to perplexity.** Because $D_{KL}\ge 0$, cross-entropy $H(p,q) \ge H(p)$ always — a model literally cannot beat the data's own irreducible entropy, no matter how well trained. This is why a language model's perplexity has a theoretical floor: it can approach the true entropy of natural language, never fall meaningfully below it.

## Practical pattern

When training a classifier or language model, the loss is usually a cross-entropy between the target distribution and the model's predicted distribution. Minimizing that loss means matching the model's probabilities to the observed reality as closely as possible.

## Common traps

- confusing entropy with cross-entropy;
- treating NLL as a vague “error” rather than a principled surprise measure;
- forgetting that the model is penalized more for confident mistakes;
- mistaking perplexity for a literal number of choices rather than an effective uncertainty measure.

## Takeaways

- Surprise is measured by $-\log p$.
- NLL is total surprise over a dataset.
- Entropy is the irreducible uncertainty under the true distribution.
- Cross-entropy is the actual training loss when the model's distribution differs from the truth.
