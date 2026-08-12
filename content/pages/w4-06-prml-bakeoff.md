---
id: w4-06-prml-bakeoff
title: "The PRML Bake-Off: Measuring the Difference"
week: 4
topic: "Act II: The Derivative Artifacts — and the Proof"
order: 6
summary: A live experiment on Bishop's PRML textbook indexes raw chunks against factoids and QA pairs and asks why polynomial regression overfits, turning the week's claim from assertion into measurement.
---

We stop asserting and start measuring. The corpus is Christopher Bishop's *Pattern Recognition and Machine Learning* (PRML) — its opening polynomial curve-fitting narrative of §1.1 through the model-selection and bias–variance material of the first three chapters. We ask it one of its own central questions:

> Why does polynomial regression overfit on a small dataset?

> PRML is the ideal villain here. Bishop never answers this in one sentence — he *shows* it: fits $M = 0, 1, 3, 9$; displays the $M=9$ curve thrashing through every point; tabulates the coefficients $w^\star$ exploding to enormous magnitudes; and only then introduces regularization. It is a textbook written for Meera, and we are about to ask it a Ravi question.

## The experiment

**Baseline.** Parse PRML, chunk it, embed the chunks. Ask the question. What comes back is very likely a single chunk describing the wiggling curve, or the regularization formula — but rarely the self-contained causal claim "a high-degree polynomial has more free parameters than data points, so it fits the noise, and its coefficients blow up." That sentence exists nowhere in Bishop as a sentence; it is distributed across a figure, a table, and three paragraphs.

**Derivative indices.** Generate factoids and three-to-eight QA pairs per chunk over the same chapters — "Q: why do the weights become large when the model is too flexible? A: …" — embed those, and ask again. The retrieved object is now query-shaped and self-contained.

## Three rules that keep the bake-off honest

A strong embedder on a lexically rich query can make the naive baseline look better than it is. A deflated demo teaches nothing, so:

1. **Use queries with real vocabulary mismatch.** Bishop writes "coefficients become large"; a student asks "why do the weights blow up when the curve gets too wiggly?" The derived path has normalized that dialect; the raw chunks have not.
2. **Include synthesis queries.** "What is the relationship between model complexity, dataset size, and overfitting here?" spans three chunks. Raw chunking returns one fragment; the derived path — and later RAPTOR — assembles the whole.
3. **Score answer-ability, not topical relevance.** The question is not "did a related chunk come back" but "could you actually answer, self-contained, from what came back?"

## The quiet part, said out loud

Of course we still search the raw chunks. The bake-off is not derived-**instead-of**-raw; it is derived-**in-addition-to**-raw. The raw-chunk index never leaves the system. Some queries — "what does §4.2 actually say?" — are best served by the original passage, and the raw index is exactly where they land.

| Query band | Raw chunks | Factoids / QA pairs |
|---|---|---|
| Pointed factual | holds its own | strong |
| Vocabulary-mismatch | weak — disjoint vocabulary | pulls ahead |
| Synthesis (spans chunks) | fragment only | still struggles — RAPTOR is what actually earns its keep here |

We are not demolishing last week's work. We are giving it colleagues.
