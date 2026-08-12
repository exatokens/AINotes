---
id: w2-04-fuzzy-lookup
title: "Attention as Fuzzy Dictionary Lookup: Four Exercises"
week: 2
topic: "Act II: The Lookup That Learns"
order: 4
summary: Attention is the fuzzy lookup you already perform every time you type a misspelled word into a dictionary — distribute a unit of attention over the nearby known words, weighted by proximity, and read off a blended meaning.
---

Last week we called attention "a context giving differential emphasis to its parts." Today we make that precise, starting from something everyone has done a thousand times: searching for a word you cannot quite spell. Imagine a dictionary website. Type a word that isn't there, and a good search doesn't fail — it finds the nearby words it knows and offers their meanings, weighted by closeness. That act of fuzzy lookup **is** attention. Let's do four, by hand, and watch our own minds.

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
