---
id: w2-01-softmax-temperature
title: "Softmax, Built by Hand — and the Temperature Knob"
week: 2
topic: "Act I: The Shape of a Decision"
order: 1
summary: The softmax turns a fistful of raw logits into a lawful probability distribution by exponentiating and normalizing, and one hidden knob, temperature, dials the result between a hard snap and a shrug without ever changing what the machine prefers.
---

Suppose a small vision model looks at a photograph and emits three raw scores — **logits** — for the three things it has been taught to recognise: a cow, a duck, a sofa. Say the numbers are $2.0$, $1.0$, and $0.1$. These are honest reports of the model's enthusiasm, but they are useless as a decision: they don't sum to anything in particular, one could have been negative, and there's no sense in which the cow "owns" 2.0 units of belief. We want to turn raw enthusiasm into something we could bet on — a distribution that sums to one.

## The two-step ritual

**Step one, exponentiate.** Replace each logit $z_i$ by $e^{z_i}$. Three things happen at once. Every exponential is positive, so a negative logit can no longer embarrass us. The exponential is monotonic, so it never reorders the bars — the cow was tallest and stays tallest. And the exponential amplifies gaps: a logit lead of 1.0 becomes a multiplicative lead of $e \approx 2.718$. Here, $e^{2.0}\approx 7.39$, $e^{1.0}\approx 2.72$, $e^{0.1}\approx 1.11$.

**Step two, normalise.** Divide each exponential by their sum, $7.39+2.72+1.11=11.22$, giving $[0.659, 0.242, 0.099]$ — a proper distribution. Written out, this is the softmax:

$$\text{softmax}(z)_i = \frac{e^{z_i}}{\sum_j e^{z_j}}$$

> An old physicist's habit: whenever a quantity is divided by the sum of all such quantities, suspect a conservation law. Probability mass behaves like an incompressible fluid — there is exactly one unit of it, and the softmax only decides how to apportion that unit among the candidates. Push more onto the cow and less remains for the duck; nothing is created or destroyed, only redistributed.

Where do the logits come from? In a real classifier, the photograph is already an embedding — a point on last week's globe — and each candidate class owns its own vector too. The logit for "cow" is the dot product of the image's embedding with the cow class vector: how aligned the picture is with the idea of a cow. The softmax doesn't act on numbers from nowhere; it acts on **geometric alignments**, turning "how close is this to each concept" into "how probable is each concept."

The name is a small slander: the softmax is not a soft *max* — it returns a soft **argmax**, a smeared, differentiable pointing-at the largest entry. The hard argmax has a gradient of zero almost everywhere and is useless to gradient descent; the softmax is its smooth, learnable cousin.

## The temperature knob

Insert a positive number $T$, the temperature, and divide every logit by it before exponentiating:

$$\text{softmax}_T(z)_i = \frac{e^{z_i/T}}{\sum_j e^{z_j/T}}$$

At $T=1$ this is the plain softmax above. The education is in the extremes. As $T \to 0$, the divided logits spread apart astronomically and the distribution snaps onto the single largest logit — a hard, near-deterministic decision. As $T \to \infty$, the divided logits collapse toward equality and the distribution relaxes to uniform — a shrug. Because dividing by a positive constant never reorders the bars, **temperature never changes what the machine prefers, only how hard it presses on that preference.**

| $T$ | cow | duck | sofa | character |
|---|---|---|---|---|
| 0.25 | 0.978 | 0.018 | 0.004 | nearly a hard argmax |
| 0.5 | 0.866 | 0.117 | 0.017 | confident |
| 1.0 | 0.659 | 0.242 | 0.099 | the plain softmax |
| 2.0 | 0.484 | 0.293 | 0.223 | hedging |
| 10 | 0.371 | 0.336 | 0.293 | almost a shrug |

This is exactly the "creativity" slider in a chatbot's settings: low temperature repeats the single most likely next token, dependable and dull; high temperature lets long-shot tokens through, surprising and sometimes unhinged. Same knob, same exponential, same conservation law.

## Keeping the softmax sane

One practical trap: if a logit is large, say 1000, $e^{1000}$ overflows to infinity and the whole distribution becomes NaN. The cure exploits an invariance — the softmax is unchanged if you subtract the same constant from every logit first, because it cancels top and bottom:

$$\text{softmax}(z)_i = \frac{e^{\,z_i - \max_j z_j}}{\sum_k e^{\,z_k - \max_j z_j}}$$

Now the largest exponent is exactly zero, nothing overflows, and the answer is bit-for-bit identical. Every production softmax on earth does this.

```python
# softmax and temperature, by hand, on the cow-duck-sofa logits
import math

logits = [2.0, 1.0, 0.1]

def softmax_T(z, T=1.0):
    m = max(z)                                   # numerical-stability trick
    exps = [math.exp((zi - m) / T) for zi in z]
    total = sum(exps)
    return [e / total for e in exps]

for T in [0.25, 0.5, 1.0, 2.0, 10]:
    print(T, [round(p, 3) for p in softmax_T(logits, T)])
```

> **Hold this thought:** temperature is not a loose metaphor. The same knob that controls a chatbot's confidence will reappear this afternoon, uninvited, in the $\sqrt{d}$ buried inside the attention equation — dividing attention scores before their softmax is turning the very same knob. Keep a corner of your mind on it.
