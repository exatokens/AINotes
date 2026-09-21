---
id: w2-06-self-attention-qkv
title: "Self-Attention Revisited: Query, Key, Value, and a Worked Example"
week: 2
topic: "Act II: The Lookup That Learns"
order: 6
summary: A word resolves its own ambiguity by scoring a query formed from itself against the keys of its sentence-mates and reading back a softmax-weighted blend of their values — the fuzzy dictionary lookup, turned inward and made differentiable.
---

## Core intuition

Self-attention is the same fuzzy lookup principle, but now the dictionary lives inside the sentence itself. A token asks, “Which nearby tokens matter most to me, in this context?” and then blends their information into a new contextual representation.

This is how a model resolves ambiguity: it does not decide the meaning of “bank” in advance; it computes it from the observed context.

## Why it matters

This chapter is the heart of the transformer. The model is not just storing vectors; it is dynamically selecting which context to read and how much weight to give each source.

That mechanism is what enables contextual meaning, disambiguation, and the step from static embeddings to powerful language models.

## Instructor framing

This is the moment where the earlier fuzzy-dictionary intuition becomes the actual transformer computation. The course is moving from “words are vectors” to “words are queries over their context.”

## Worked example


Take the sentence “She swam across the river to the other bank.” Here, the word “bank” should be interpreted as a riverside edge, not a financial institution. Self-attention gives it a contextual meaning by attending to nearby words like “river” and “across.”

That contextualization is the engine behind the machine’s ability to understand polysemy.

## A word looks up its own meaning

In the dictionary exercises, the keys were an external reference book. Now the move that changed everything: consider

> She swam across the river to the other **bank**.

In isolation, *bank* is hopelessly ambiguous — a place that keeps money, or the edge of a river. How does it discover which, here? Not by consulting all of English — only by consulting the other words in its own sentence. *Bank*'s "dictionary" shrinks from all of English to just $[\text{she, swam, across, the, river, to, the, other, bank}]$. The word forms a query from itself, scores that query against the key of every word in the sentence (including itself — the mirror), turns the scores into a softmax distribution, and reads back a blended value: a new, contextualised meaning.

$$\text{ctx\_meaning}(\text{bank}) = \sum_i s_i v_i, \qquad s_i = \text{softmax}\!\left(\frac{\langle k_i, q\rangle}{\sqrt{d}}\right)$$

Because the river words win most of the mass, *bank*'s contextual meaning is pulled firmly toward the water. This is the resolution of the polysemy problem from last week: a static embedding gives one frozen vector per word; self-attention gives a contextual one, recomputed fresh for every sentence.

## Query, key, value: three questions a word asks

A single word vector is asked to play three roles in the lookup, and answers each with a different learned projection of itself — three small matrices, $W_Q, W_K, W_V$, shaped by training:

| Symbol | Question it answers |
|---|---|
| $q = W_Q x$ | "What am I looking for?" — *bank* broadcasts: is there water near me, or money? |
| $k = W_K x$ | "What do I offer as a match?" — *river* advertises: I am about water |
| $v = W_V x$ | "What meaning do I contribute, if chosen?" — the payload poured into the blend |

Splitting key from value is the subtle, powerful part: a word can be a strong match for a query while contributing a meaning quite different from what made it match — just as, in a library, the catalogue card you search by (the key) is not the book you carry home (the value). This separation is what lets attention retrieve nuanced, blended meanings rather than echoing back the search terms.

## A worked attention, end to end

Take *bank* resolving itself against two context words, *river* and *money*, in a toy two-dimensional space. Let bank's query be $q=(1.0,0.0)$ — "I lean water." Let the keys be $k_{riv}=(1.0,0.2)$, $k_{mon}=(0.1,1.0)$, and the values (the meanings each would contribute) be $v_{riv}=(0.9,0.1)$ and $v_{mon}=(0.1,0.9)$.

**Score:** $\langle q,k_{riv}\rangle = 1.0$, $\langle q,k_{mon}\rangle = 0.1$.
**Scale** by $\sqrt{d}=\sqrt{2}\approx1.414$: scores become $0.707$ and $0.071$.
**Softmax:** $e^{0.707}\approx2.028$, $e^{0.071}\approx1.074$, summing to $3.102$: weights $s_{riv}\approx0.654$, $s_{mon}\approx0.346$.
**Retrieve:** $\text{ctx(bank)} = 0.654\,v_{riv} + 0.346\,v_{mon} = (0.62, 0.38)$.

The contextual meaning of *bank* lands nearer the water meaning $(0.9,0.1)$ than the finance meaning — exactly as the river context demanded — but carries a real tint of finance, because softmax never zeroes anything out.

```python
# the full worked example above, reproduced numerically
import math

q = (1.0, 0.0)
keys = {"river": (1.0, 0.2), "money": (0.1, 1.0)}
values = {"river": (0.9, 0.1), "money": (0.1, 0.9)}
d = len(q)

scores = {name: sum(a*b for a, b in zip(q, k)) / math.sqrt(d) for name, k in keys.items()}
exps = {name: math.exp(s) for name, s in scores.items()}
total = sum(exps.values())
weights = {name: e / total for name, e in exps.items()}
ctx = [sum(weights[name] * v[i] for name, v in values.items()) for i in range(d)]

print("weights:", {k: round(v, 3) for k, v in weights.items()})
print("contextual meaning of 'bank':", [round(c, 2) for c in ctx])
```

## The famous equation, in full

$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

$QK^\top$ scores every query against every key by dot product — a whole grid of proximities in one matrix multiply. Dividing by $\sqrt{d_k}$ is the temperature knob, keeping scores from snapping too hard. The softmax turns each row into an honest distribution. Multiplying by $V$ retrieves, for each query, the proximity-weighted blend of values. Query, key, value; score, normalise, retrieve — the four fuzzy-dictionary exercises, written in linear algebra and done in parallel for every word at once.

Recall last week's encoder–decoder scaffold: the decoder writes one word at a time, and the probability of a whole output sequence factorises autoregressively,

$$p(y_1,\dots,y_T) = \prod_{t=1}^{T} p(y_t \mid y_{<t}, x)$$

— the product of probabilities again, the very object turned into a sum of log-likelihoods on the previous page. Training a sequence model is minimising the NLL of this factorisation. The old bottleneck design forced every $p(y_t\mid y_{<t},x)$ through one cramped vector; Bahdanau's insight let the decoder attend back over all encoder states instead. The transformer takes that idea to its conclusion: the bottleneck dissolves entirely, and "Attention is all you need" — keep the attention, throw away the recurrent scaffolding, lose nothing.

A real transformer runs several attention heads in parallel, each projecting into its own subspace and attending for its own kind of relationship, then concatenates the results — several specialist dictionaries consulted at once. And raw attention, as written above, is permutation-blind: shuffle the sentence and the weights don't change, which is why **positional encoding** (stamping each token with its place in line) is needed to restore word order.

> **Why the $\sqrt{d}$?** The paper's own modest reason: it keeps dot products from growing too large and saturating the softmax. A sharper reason follows from concentration of measure (Week 1): the dot product of two random $d$-dimensional vectors has a typical spread of order $\sqrt{d}$. Left undivided, attention scores would grow colder — snapping harder onto a single key — as dimension increases. Dividing by $\sqrt{d_k}$ holds the softmax's temperature constant as $d$ grows. It is not a numerical footnote; it is a thermostat.



## Math explained step by step

Recap the *bank* computation above as the four moves of $\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$, each with its "why":

**Step 1 — project, don't reuse, the raw vector.** *Bank* doesn't ask its question with its own raw embedding; it applies a learned matrix, $q = W_Q x$, to produce a query. Why bother? Because the same underlying vector needs to play three different roles (asking, matching, contributing), and one fixed vector cannot ask a good question and also be a good answer — separate projections let it specialise.

**Step 2 — score against every key with a dot product, then rescale.** $\langle q, k_i \rangle$ measures alignment between what *bank* is looking for and what each neighbour offers ($1.0$ for *river*, $0.1$ for *money*, in the worked numbers above). Dividing by $\sqrt{d_k}$ exists because — as concentration of measure showed in Week 1 — dot products of longer vectors grow larger just from having more terms, not from being more relevant; without the rescale, the softmax below would saturate for the wrong reason as dimension grows.

**Step 3 — softmax the scores into real weights.** $0.707$ and $0.071$ become $0.654$ and $0.346$: a genuine distribution, so "how much does each neighbour matter" is answerable as a number that sums to one, not an unbounded score.

**Step 4 — read off a blend of values, not keys.** The output is $\sum_i s_i v_i$, using each word's *value*, not its key. This is why splitting key from value matters: a word can be the right match (high key-score) while contributing a payload (value) that differs from what made it match — the catalogue card is not the book.

## Practical pattern

In an actual transformer, each layer computes several attention heads in parallel and projects the result into multiple subspaces. This allows the model to attend for different kinds of relations at the same time: syntax, coreference, semantics, and more.

## Common traps

- forgetting that the query, key, and value roles are distinct;
- assuming attention is just a direct similarity matrix with no learned projections;
- ignoring that the temperature scaling by $\sqrt{d_k}$ matters for stability;
- treating attention as “magic” rather than a weighted lookup over context.

## Takeaways

- Self-attention is contextual fuzzy lookup.
- Query, key, and value projections define what is searched, how similarity is scored, and what is aggregated.
- The softmax distribution determines how much each token contributes.
- Transformer layers then stack these contextual updates across depth.
