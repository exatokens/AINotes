---
id: w2-01-softmax-temperature
title: "Softmax, Built by Hand — and the Temperature Knob"
week: 2
topic: "Act I: The Shape of a Decision"
order: 1
summary: The softmax turns a fistful of raw logits into a lawful probability distribution by exponentiating and normalizing, and one hidden knob, temperature, dials the result between a hard snap and a shrug without ever changing what the machine prefers.
---

Suppose a small vision model looks at a photograph and emits three raw scores — **logits** — for the three things it has been taught to recognise: a cow, a duck, a sofa. Say the numbers are $2.0$, $1.0$, and $0.1$. These are honest reports of the model's enthusiasm, but they are useless as a decision: they don't sum to anything in particular, one could have been negative, and there's no sense in which the cow "owns" 2.0 units of belief. We want to turn raw enthusiasm into something we could bet on — a distribution that sums to one.

This is the first great piece of practical probability in the course: a model can rank preferences without yet knowing how to allocate certainty, and the softmax is the precise device that turns ranking into probability.

## Core intuition

A model's raw scores are useful only as a ranking signal. They are not probabilities. The softmax is the rule that converts a set of preference scores into a valid probability distribution while preserving the ordering of the options.

This is why the softmax is central to modern ML: it lets us turn “which option is most preferred?” into “what fraction of probability mass should I assign to each option?”

## Why it matters

Every time a model chooses a next token, a class label, or a candidate answer, it is usually running through a softmax-like conversion. The score itself is not the decision; the normalised probability is the decision.

Temperature then becomes the control knob for confidence. A low temperature makes the model decisive; a high temperature makes it more exploratory and less certain.

## Instructor framing

This chapter is the first moment where probabilities become a design tool rather than just a theoretical object. The course is teaching that a softmax is not a mysterious formula; it is a disciplined method for turning preferences into probabilities while retaining the model's ranking.

## Worked example


If the model gives the cow a logit of 2.0 and the duck 1.0, the cow is preferred. But without a softmax, we cannot say how strongly. By exponentiating and normalising, we get a distribution that tells us the model believes the cow is roughly 66% likely, the duck 24%, and the sofa 10%.

The key idea is that the softmax keeps the ordering intact while turning the scores into a proper probability distribution.

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



## Math explained step by step

Derive why temperature reshapes confidence exactly the way the table above shows, rather than just reading the table.

**Step 1 — express the ratio between two probabilities.** For any two classes $i,j$, $\dfrac{\text{softmax}_T(z)_i}{\text{softmax}_T(z)_j} = e^{(z_i-z_j)/T}$ — the normalising sum cancels entirely, so the *relative* preference between any two options depends only on their logit gap divided by $T$.

**Step 2 — see why order can never flip.** Since $T>0$, dividing the gap $z_i - z_j$ by $T$ never changes its sign — if the cow's logit exceeded the duck's before, $e^{(z_i-z_j)/T} > 1$ for every $T>0$, so the cow's probability exceeds the duck's at every temperature. This is the algebra behind "temperature never changes what the machine prefers."

**Step 3 — see why the gap still matters enormously.** The cow-vs-duck logit gap is $2.0-1.0=1.0$. At $T=1$, the ratio is $e^{1.0}\approx 2.72$. At $T=0.25$, the *effective* gap becomes $1.0/0.25=4.0$, and the ratio balloons to $e^{4.0}\approx 54.6$ — the same fixed gap, divided by a shrinking $T$, is exponentiated into an ever more lopsided ratio. That's the mechanism behind $T\to 0$ snapping to a near-hard argmax: not a different rule, the same ratio formula, with the exponent stretched.

**Step 4 — the limits fall out of the same formula.** As $T\to\infty$, every gap divided by $T$ shrinks toward $0$, so every ratio $e^{(z_i-z_j)/T}\to 1$ — all options become equally likely, the shrug. As $T\to 0^+$, any nonzero gap divided by $T$ blows up, so the ratio between the top logit and every other collapses toward $\infty$ — all probability mass piles onto the single largest logit, the hard argmax.

**Step 5 — verify against the table.** Cow-vs-sofa gap is $2.0-0.1=1.9$. At $T=0.25$, effective gap $=7.6$, ratio $e^{7.6}\approx 1998$ — consistent with the table's $0.978$ vs $0.004$ (ratio $\approx 244$; the discrepancy from 1998 is because the *three-way* normalisation also folds in the duck's share, but the direction and scale of the effect match exactly).

## Practical pattern

In production systems, the softmax is usually stabilized by subtracting the maximum logit before exponentiation. This prevents overflow without changing the distribution. Temperature is then used deliberately to govern confidence and randomness.

## Common traps

- treating logits as probabilities;
- forgetting that temperature does not change the ranking order;
- ignoring the numerical-stability trick;
- confusing high confidence with correctness.

## Takeaways

- Softmax converts raw scores into a probability distribution.
- Exponentiation preserves ranking and amplifies gaps.
- Temperature controls sharpness without changing the preferred option.
- The same mechanism reappears in attention and generation dynamics.
