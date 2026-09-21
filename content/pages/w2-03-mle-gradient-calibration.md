---
id: w2-03-mle-gradient-calibration
title: "Maximum Likelihood, the Gradient of Cross-Entropy, and Calibration"
week: 2
topic: "Act I: The Shape of a Decision"
order: 3
summary: Softmax paired with negative log-likelihood yields a gradient of disarming simplicity, predicted minus actual, and that same logarithm turns out to be forced rather than chosen — the only continuous repair that keeps a billion-term likelihood product computable at all.
---

## Core intuition

The softmax and the negative log-likelihood are a matched pair. The softmax turns raw scores into probabilities, and the log-loss converts those probabilities into a training signal that teaches the model how wrong it was.

This is one of the reasons neural networks became practical: the learning signal is not messy or ad hoc. It is a clean “predicted minus actual” correction, and that simplicity is exactly what made the whole optimisation pipeline tractable.

## Why it matters

Without this pairing, training would be unstable and the gradients would be awkward or impossible to optimize. The design choice is not arbitrary — it is exactly what makes gradient descent on deep networks work at scale.

This is also why the model can be trained from data: the loss measures how surprised it was by the true outcome, and the gradient tells it how to reduce that surprise.

## Instructor framing

This chapter is the bridge from probability to learning. We have seen how the model makes a decision; now we see how it learns from the mismatch between its decision and the truth.

## Worked example


If the model predicts a distribution $p=[0.7, 0.2, 0.1]$ for a correct class whose target is $y=[1,0,0]$, then the gradient on the correct class is $0.7-1=-0.3$, while the wrong classes receive positive updates. This means the model is nudged upward on the correct answer and downward on the alternatives.

The learning rule is therefore direct and mathematically clean.

## The gradient the softmax allows

Why did softmax-in-front, negative-log-likelihood-behind become the universal pairing in virtually every classifier on earth? Let the true answer be a one-hot vector $y$ (a one on the correct class, zeros elsewhere), let $p=\text{softmax}(z)$ be the predicted distribution, and let the loss be the cross-entropy $-\sum_i y_i \log p_i$. The gradient of that loss with respect to the logits is

$$\frac{\partial L}{\partial z} = p - y$$

Stop and admire how clean that is. The signal that flows back to teach the network is **predicted minus actual** — the error itself, naked, with no awkward factors. If the model put 0.7 on the right class, the gradient there is $0.7-1=-0.3$, a gentle pull upward; if it put 0.9 on a wrong class, the gradient there is $0.9-0=0.9$, a firm shove down. The exponential of the softmax and the logarithm of the loss were built for each other — the log undoes the exp at exactly the right moment.

```python
# gradient of cross-entropy w.r.t. logits: p - y, on a 3-class toy example
import math

logits = [2.0, 1.0, 0.1]
true_class = 0   # "cow" is correct

exps = [math.exp(z) for z in logits]
p = [e / sum(exps) for e in exps]
y = [1.0 if i == true_class else 0.0 for i in range(len(logits))]
grad = [pi - yi for pi, yi in zip(p, y)]
print("p:", [round(v, 3) for v in p])
print("gradient p - y:", [round(g, 3) for g in grad])
```

## Is a 0.7 really a 70%? A word on calibration

The softmax always hands back something that *looks* like a probability — it sums to one — but looking like one and being one are different things. A model is **calibrated** if, among all the times it says "0.7," the answer really is correct about 70% of the time. Modern deep networks, trained hard to minimise NLL, learn to push their winning logit very high, so a reported 0.99 may correspond to a true accuracy of only 0.90.

This matters directly for retrieval: the moment you threshold on a score — "only answer if the model is at least 0.8 confident," "only retrieve if similarity exceeds this cut" — you're betting the number means what it says. An uncalibrated model quietly breaks that bet: a grounding judge that trusts an overconfident 0.95 will wave through hallucinations; a retriever with a miscalibrated cut-off will drop good documents or admit bad ones. The standard cure is **temperature scaling** — fitting a single $T>1$ on held-out data and dividing the logits by it before the softmax. It cannot change which class wins (a positive divisor never reorders), but it cools the distribution until confidence matches accuracy.

## Emily's objection: why the logarithm is forced, not chosen

A careful objection: "You dragged the surprise floor from 1 down to 0 using the logarithm. But $1/p - 1$ is also zero at $p=1$ and also blows up near zero. Why the log and not the simpler subtraction?"

The answer requires thinking about the evidence as a whole, not one event at a time. If events are independent, the probability your beliefs would have produced exactly the observed sequence is the product of the individual probabilities — for a corpus of $N$ outcomes,

$$L = \prod_{k=1}^{N} p_k$$

This is the **likelihood**, and the principle of **Maximum Likelihood Estimation (MLE)** says: the best model is the one that makes the observed evidence most probable — the one that maximises $L$.

Two problems sink maximising $L$ directly, and one move solves both. First, computationally: multiply a hundred random numbers between zero and one, and the result underflows to something like $10^{-40}$ — a dead, gradientless zero on any real floating-point system. A real corpus has billions of factors; the product underflows within a few hundred terms. Second, is there a transformation that tames this without moving the maximum? The logarithm is monotonic, so the value that maximises $L$ also maximises $\log L$ — and crucially, it turns a product into a sum:

$$\log L = \log\prod_k p_k = \sum_k \log p_k$$

An unrepresentable product becomes a perfectly civilised sum. Maximise $\log L$; or, since optimisers descend rather than climb, minimise its negative, $-\log L = -\sum_k \log p_k$ — precisely the negative log-likelihood built from rainy afternoons a page ago.

> Why the log and not $1/p - 1$? Because $1/p-1$ never turns the product into a sum — it leaves you stranded with an unrepresentable product. The logarithm is, up to an overall choice of base, the *unique* continuous function converting products into sums (a fact known as Cauchy's functional equation: the only continuous $f$ with $f(ab)=f(a)+f(b)$ is a logarithm). The intuitive demand — that independent surprises should add — and the rigorous demand — that the likelihood product become a computable sum — turn out to be the same demand. The log was never a convenience; it was forced.

```python
# why a product of probabilities is the wrong object to optimise
import random, math

random.seed(0)
probs = [random.random() for _ in range(100)]

product = 1.0
for p in probs:
    product *= p
log_sum = sum(math.log(p) for p in probs)

print("raw product (underflows toward 0):", product)
print("sum of logs (perfectly representable):", round(log_sum, 3))
print("exp(sum of logs) recovers the product:", math.exp(log_sum))
```



## Math explained step by step

The page states the punchline, $\partial L/\partial z = p - y$; derive it from the chain rule so the "disarming simplicity" is earned, not asserted.

**Step 1 — set up the chain rule.** The loss depends on the logits $z$ only through the probabilities $p=\text{softmax}(z)$, so $\dfrac{\partial L}{\partial z_i} = \sum_k \dfrac{\partial L}{\partial p_k}\dfrac{\partial p_k}{\partial z_i}$ — every probability that depends on $z_i$ contributes a term.

**Step 2 — differentiate the cross-entropy loss w.r.t. the probabilities.** With $L=-\sum_k y_k \log p_k$, $\dfrac{\partial L}{\partial p_k} = -\dfrac{y_k}{p_k}$.

**Step 3 — differentiate the softmax itself.** This is the one genuinely subtle step, because $p_k$ depends on *every* logit through the shared normalising sum, not just $z_k$. Direct differentiation of $p_k = e^{z_k}/\sum_j e^{z_j}$ gives two cases: $\dfrac{\partial p_k}{\partial z_i} = p_k(1-p_i)$ when $k=i$ (raising $z_i$ raises $p_i$ but also inflates the shared denominator, which pulls $p_i$ back down slightly), and $\dfrac{\partial p_k}{\partial z_i} = -p_k p_i$ when $k\ne i$ (raising $z_i$ only inflates the shared denominator, which pulls every *other* probability down).

**Step 4 — combine the two cases in the sum from Step 1.** Splitting the sum into the $k=i$ term and the $k\ne i$ terms: $\dfrac{\partial L}{\partial z_i} = -\dfrac{y_i}{p_i}\cdot p_i(1-p_i) \;-\!\!\sum_{k\ne i} \left(-\dfrac{y_k}{p_k}\right)(-p_k p_i) = -y_i(1-p_i) - p_i\sum_{k\ne i} y_k$.

**Step 5 — collapse using $\sum_k y_k = 1$.** Since $y$ is one-hot, $\sum_{k\ne i} y_k = 1-y_i$. Substituting: $\dfrac{\partial L}{\partial z_i} = -y_i + y_i p_i - p_i(1-y_i) = -y_i + y_ip_i - p_i + p_iy_i = p_i - y_i$ — the two $y_ip_i$ terms cancel exactly, and everything else collapses to the clean difference. The elaborate softmax derivative and the elaborate cross-entropy derivative were built so that, multiplied together and summed, almost everything cancels — that cancellation, not coincidence, is why this pairing became universal.

## Practical pattern

In practice, the model is trained to minimize the cross-entropy, and the gradient is the simple difference between predicted and target probabilities. That is the reason neural networks can learn from large datasets without any bespoke manual rule for each class.

## Common traps

- interpreting logits as probabilities;
- ignoring calibration and overconfidence;
- mistaking a large probability for true correctness;
- forgetting that the log transform is used because it makes products tractable and additive.

## Takeaways

- Softmax + cross-entropy gives a clean learning signal.
- The gradient is simply predicted minus target.
- Maximum likelihood requires a representable objective, which forces the logarithm.
- Calibration matters because probabilities are only useful when they track reality.
