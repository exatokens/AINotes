---
id: w2-04-fuzzy-lookup
title: "Attention as Fuzzy Dictionary Lookup: Four Exercises"
week: 2
topic: "Act II: The Lookup That Learns"
order: 4
summary: Attention is the fuzzy lookup you already perform every time you type a misspelled word into a dictionary — distribute a unit of attention over the nearby known words, weighted by proximity, and read off a blended meaning.
---

Last week we called attention "a context giving differential emphasis to its parts." Today we make that precise, starting from something everyone has done a thousand times: searching for a word you cannot quite spell. Imagine a dictionary website. Type a word that isn't there, and a good search doesn't fail — it finds the nearby words it knows and offers their meanings, weighted by closeness. That act of fuzzy lookup **is** attention. Let's do four, by hand, and watch our own minds.

The nicest way to understand attention is to see it as a weighted retrieval operation over keys and values; the model is not doing magic, it is performing a smooth, learned lookup.

## Core intuition

Attention is a fuzzy dictionary lookup. A query points to nearby keys, the system assigns weights to them, and then it blends the corresponding values together.

This is not metaphorical. It's the exact operation that modern attention performs, just made differentiable and generalized to many tokens at once.

## Why it matters

Without this view, attention appears mysterious. Once you see it as a search over nearby candidates, the mechanism becomes much easier to reason about and much easier to debug.

This is the foundation of contextual encoding: the model does not read a word in isolation, but looks up the relevant neighboring signals and blends them together.

## Instructor framing

The chapter is transforming the conceptual puzzle from “what is attention?” into “what kind of computation is attention?” The answer is that it is a learned, soft, weighted retrieval procedure over context.

## Worked example


Suppose you type “teh” instead of “the.” A fuzzy lookup does not require an exact match; it scores the nearby entries and produces a distribution over candidates. The best match gets most of the mass, but other plausible candidates still contribute a little.

The result is a smooth, informative retrieval rather than a brittle exact lookup.

| Exercise | You type | Candidates | Typical weights | The lesson |
|---|---|---|---|---|
| 1 — high-confidence match | recieve | receive, relieve, recipe | [0.95, 0.04, 0.01] | a near-certain bet, retrieved meaning is mostly one candidate's |
| 2 — split attention | accross | access, across, actress | [0.40, 0.35, 0.25] | a genuine hedge — the softmax faithfully reports real ambiguity |
| 3 — the keystone | teh | the, ten, tea | [0.85, 0.10, 0.05] | edit distance ties all three; your score encodes learned priors, not raw distance |
| 4 — structure and stem | runnign | running, run, ruin | [0.85, 0.10, 0.05] | you did morphology (stemming, prefix-matching) without being asked |

In Exercise 1, you've computed a softmax over proximity scores and retrieved a blended value — you didn't know you were doing attention, but you were.

Exercise 3 is the keystone. Measured by raw edit distance, *the*, *ten*, and *tea* are all roughly equidistant from *teh*. A system that scored only by edit distance would shrug and return $[0.33, 0.33, 0.33]$. But you almost certainly gave something like $[0.85, 0.10, 0.05]$ — overwhelmingly favouring *the* — because *teh* is one of the most common typos in English: a transposition slip your fingers make constantly, while *teh→ten* or *teh→tea* as slips are far rarer. Your score encodes not the geometry of the keyboard alone but **the statistics of human error** — a learned prior. This is the precise sense in which trained attention is richer than any hand-coded distance: the dot product $\langle q,k \rangle$ that scores a query against a key is itself *learned*, so it can discover that *the* deserves the mass even when a ruler says all three are equally far. Edit distance is geometry; attention is geometry plus everything the model has ever learned about which confusions are likely.

Exercise 4 shows the same thing from another angle: you recognised a transposed ending (*-ign* for *-ing*), noticed the shared stem *run*, and let *ruin* in only as a grudging long shot. Real subword tokenizers and real attention heads rediscover exactly these regularities — because words sharing a token (*running*, *runner*, *runs* all containing *run*) begin life as neighbours, sharing a fragment and therefore a gradient.

> **The lesson, stated once and for keeps:** when an exact match fails, look at the nearby keys ($K$) and their meanings ($V$), and weight the meanings by each key's proximity to your query ($Q$). The retrieved meaning is a sum of values weighted by query–key proximity, and the weights are a softmax so they form an honest distribution. That is the core insight of "Attention Is All You Need," stripped of notation and handed back to you as something you already knew how to do.

```python
# reproducing Exercise 3 ("teh") — why learned priors beat raw edit distance
import math

# a hand-coded distance metric sees these as roughly tied
edit_distances = {"the": 1, "ten": 1, "tea": 1}

# but a *learned* score (standing in for a trained dot product) reflects
# how common each typo pattern actually is in practice
learned_scores = {"the": 3.0, "ten": 1.0, "tea": 0.3}  # transposition >> substitution

exps = {k: math.exp(v) for k, v in learned_scores.items()}
total = sum(exps.values())
weights = {k: v / total for k, v in exps.items()}
print("softmax over learned scores:", {k: round(v, 3) for k, v in weights.items()})
# edit distance alone would have returned an uninformative [0.33, 0.33, 0.33]
```



## Math explained step by step

Turn the four exercises into the four steps every attention computation performs, in order:

**Step 1 — form a query.** "Teh" is the query: the thing you're trying to place a meaning on. In a real model, this is a learned projection $q = W_Q x$ of the token's own vector — the token asking "what am I looking for?"

**Step 2 — score the query against every candidate key.** You mentally compared "teh" against "the," "ten," and "tea." A model does the same with a dot product, $\langle q, k_i\rangle$, between the query and each candidate's key vector. Crucially — this is the point Exercise 3 makes — the score is not raw edit distance; it is a *learned* dot product, so it can encode "transpositions are more common than substitutions" the way you unconsciously did.

**Step 3 — turn scores into a distribution with softmax.** Raw scores $[3.0, 1.0, 0.3]$ (favoring "the") are not weights yet — they can be any real number. Softmax exponentiates and normalises them into $[0.85, 0.10, 0.05]$: a proper distribution that still preserves which candidate scored highest, exactly as it did last week with logits.

**Step 4 — retrieve a blend, not a single answer.** The final meaning is $\sum_i s_i v_i$: each candidate's value vector, weighted by its softmax score. This is *why* the lookup is "fuzzy" — even the losing candidates leak a small amount of their meaning into the result, which is exactly right for Exercise 2's genuine ambiguity ("accross" really could be "across" or "access").

## Practical pattern

In transformer models, the query, key, and value projections allow the system to look up context in a learned way rather than through rigid lexical matching. The result is a context-sensitive representation that can encode ambiguity and structure simultaneously.

## Common traps

- assuming attention is a literal dictionary lookup over exact strings;
- forgetting that the weights are learned, not just geometric;
- conflating key matching with value retrieval;
- treating the softmax distribution as noise instead of an honest representation of uncertainty.

## Takeaways

- Attention is a fuzzy, weighted retrieval mechanism.
- Query-key interaction is the similarity signal.
- Softmax turns similarity into a probability-like allocation of attention.
- The value vectors carry the actual content to be aggregated.
