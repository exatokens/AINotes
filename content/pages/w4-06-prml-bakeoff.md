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
## Core intuition

The best way to test a retrieval strategy is not to ask whether it is lexically similar, but whether it can answer a real question that spans several related facts in the source.

## Why it matters

This experiment reveals what a raw chunk index misses and what the derivative artifacts recover. It is the empirical evidence that the design principle from the previous pages is not just clever — it is effective.

## Instructor framing

Run this bake-off live if at all possible — the pedagogical value is not in the conclusion (derived artifacts help) but in watching a real embedding model fail on a real vocabulary-mismatch query, then watching the exact same model succeed once the indexed text changes. A claimed result read from a slide convinces no one; a live failure followed by a live fix converts skeptics.

## Worked example



This is the book's proof-of-work moment. We do not merely claim that factoids and QA pairs help; we measure their effect on a canonical question from a real textbook.
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






## Math explained step by step

Turn "three rules that keep the bake-off honest" into the actual measurement logic.

**Step 1 — define what's being compared.** For each query $q$ in the test set, compute $\text{rank}_{\text{raw}}(q)$ = the position of the correct answer-bearing content in the raw-chunk index's top-$k$, and $\text{rank}_{\text{derived}}(q)$ = the same for the factoid/QA index. "Better" means a lower rank (or "found at all" versus "absent from top-$k$").

**Step 2 — see why vocabulary-mismatch queries are the discriminating test, not the confirming one.** A query using Bishop's own words ("why do coefficients become large") would let the raw chunk index win by lexical-adjacent luck, telling you nothing about whether derived artifacts help — it's testing a case neither method needs help with. The mismatch query ("why do the weights blow up when the curve gets too wiggly?") isolates exactly the capability derived artifacts add: bridging vocabulary gap through paraphrase-shaped indexing (as in the "Six Costumes" and "Meera and Ravi" pages).

**Step 3 — see why synthesis queries are a *different* axis of measurement, not a harder version of the same one.** A synthesis query ("relationship between complexity, dataset size, and overfitting") fails on raw chunks not because of vocabulary but because of *distribution* — the answer literally does not exist as one contiguous span of source text. Measuring this axis separately from vocabulary-mismatch prevents conflating two different failure modes and mis-attributing a fix.

**Step 4 — the answerability metric is the one that actually matters for RAG, and it's stricter than retrieval metrics alone.** "Did a related chunk come back" (topical recall) can be satisfied by a chunk that discusses the topic without containing the answer. "Could you actually answer, self-contained, from what came back" requires the retrieved content to be sufficient on its own — which is precisely the standard a downstream generator is held to, so measuring anything looser overstates how well the system will actually perform end-to-end.

## Practical pattern

Run this exact bake-off structure before trusting a chunking or artifact-generation change in your own system:

1. build (or reuse) a test set stratified into the three bands in the table — pointed factual, vocabulary-mismatch, and synthesis — because a single blended score hides which capability actually improved;
2. deliberately phrase vocabulary-mismatch queries in language a real end user would use, not language borrowed from the source document;
3. score answerability (can a self-contained answer be constructed from what was retrieved), not mere topical overlap — this is the metric that predicts generation quality, not just retrieval relevance;
4. keep the raw-chunk index in the comparison as a baseline permanently, not just for this one experiment — derived artifacts are additive, and the raw index remains the right tool for "what does §4.2 actually say" queries.

## Common traps

- measuring only pointed factual queries, where the baseline already performs well, and concluding derived artifacts don't help — the real gains live in the vocabulary-mismatch and synthesis bands;
- phrasing test queries using the source document's own vocabulary, which flatters the raw-chunk baseline and understates the real-world vocabulary gap;
- scoring "topically relevant chunk retrieved" instead of "self-contained answer constructable," which overstates how ready a system is for production;
- treating a bake-off as a one-time proof rather than a repeatable evaluation harness — every future chunking or artifact-generation change should be run through the same three-band test set.

## Takeaways

- The value of derived artifacts (factoids, QA pairs) shows up specifically on vocabulary-mismatch and synthesis queries, not on queries the source text already answers in the user's own words.
- Raw chunks and derived artifacts are complementary indexes, not competitors — "what does §4.2 say" queries still belong to the raw index.
- Concretely: before adopting any retrieval change, measure it against a three-band test set (pointed, vocabulary-mismatch, synthesis) scored on answerability, not topical relevance alone — a single blended metric will hide exactly where the change helped or hurt.
