---
id: w4-01-search-native-text
title: "The Understudy: When the Text You Search Is Not the Text You Show"
week: 4
topic: "Act I: The Purpose Problem"
order: 1
summary: For three weeks we indexed the author's own words; this week we manufacture new text written for the searcher, search that instead, and show the reader the original.
---

> The map is not the territory. — Alfred Korzybski

Last week we measured the size of thoughts. We chunked, catalogued the pathologies of cutting text into pieces, and weighed the remedies: semantic boundaries, hierarchical chunks, contextual retrieval, late chunking. We even asked whether to chunk at all, since a vision-language model can embed the page as an image and skip parsing entirely.

But notice what every one of those techniques quietly assumed. Each was still indexing the original text. Semantic chunking cut the original differently; contextual retrieval decorated the original with a sentence of context; late chunking pooled the original in latent space. **The substrate never changed.** We were always searching the words the author wrote.

## Core intuition

The text written for a person to read is not necessarily the text written for a search engine to retrieve. The query and the document often speak different dialects.

This is why a search system often needs derived artifacts: compressed summaries, question-answer pairs, or “search-native” rewrites that are better aligned to the user’s query shape.

## Why it matters

If the indexing text is shaped for human reading rather than retrieval, the system pays a constant mismatch penalty. A query like “what does this model do in production?” may not align well to the original prose, even if the facts are present.

The remedy is to create derived text that is optimized for the retrieval task.

## Instructor framing

This chapter is the pivot from “source text as the facts” to “search-native text as a new artifact.” The course is telling you that retrieval quality often improves when we search a representation designed for the searcher rather than the author.

## Worked example


A legal clause may say, “notwithstanding the provisions of Section 12(b), the Licensor retains the irrevocable right to terminate.” A user asks, “Can the licensor end the contract early?” The formal legal wording and the user’s question share the same meaning but little lexical overlap. Search-native text can make that relationship explicit.

This week we abandon that assumption, and the whole posture of the course shifts with it. We stop asking "how do I cut the document well?" and start asking a stranger, more powerful question:

> What if the best thing to search is text the document never literally said?

## The single thread to hold

A document is written for a reader — to be argued, defended, taught, or filed away. It is almost never written to be found by a short, blunt query typed into a search box. So before we index a document, we will manufacture new textual objects from it — **derivative artifacts** — each one written, this time, for the searcher. We will search those. And then, having found the right place, we will show the reader the original.

That last sentence is the entire week compressed:

> We search derived artifacts; we show original results.

## What this buys you, and what it costs

Every derivative artifact is a bet: pay a little extra computation and storage at ingestion time, in exchange for a much better chance that a real user's real query lands where it should. Act I spends its time making the case that this bet is necessary — that raw text actively resists search, by design, because of who it was written for. Act II builds the toolkit of artifacts and proves, on a real textbook, that the bet pays off. Act III lifts the same idea from a single passage to an entire corpus, culminating in RAPTOR.

Nothing in this week throws away last week's work. The raw-chunk index stays. We are giving it colleagues.



## Math explained step by step

Make "lexical and semantic gap between a clause and a question" a quantity, not a feeling, using the licensor example above.

**Step 1 — measure the lexical overlap directly.** "Can the licensor end the contract early?" and "notwithstanding the provisions of Section 12(b), the Licensor retains the irrevocable right to terminate" share exactly one content word in common ("licensor"/"Licensor," modulo case) out of roughly twenty content words combined — a Jaccard overlap near $1/20 = 0.05$. Any lexical (BM25-style) search scores this pair close to zero.

**Step 2 — check whether embedding alone closes the gap.** A bi-encoder trained on general text will likely place these two sentences closer than pure lexical overlap suggests, because "notwithstanding," "irrevocable right to terminate," and "end the contract early" share legal-domain semantic territory. But it is a *partial* rescue, not a full one — legalese is dense with hedges and cross-references that dilute the semantic signal the encoder has to work with (recall lexical cohesion, Week 3).

**Step 3 — quantify the remaining gap with a derived artifact.** Now compare the query against a manufactured search-native rewrite: "The licensor can terminate the contract early." Lexical overlap jumps to near-total; embedding similarity jumps too, because the derived sentence was written *in the query's own register* rather than the contract's. The gap didn't close because the embedding model got smarter — it closed because the object being compared to the query changed.

**Step 4 — see the general principle this establishes.** For any retrieval system, total similarity is a function of both *how good the encoder is* and *how close the indexed text's register already is to the query's register*. Derivative artifacts are a lever on the second factor, and — as Act II's bake-off will show numerically — often a cheaper, more reliable lever than chasing a better embedding model.

## Practical pattern

The pattern is straightforward: keep raw text for grounding and comprehension, but also generate or index derived artifacts shaped to retrieval. Search the derivative; show the original source.

## Common traps

- assuming the author’s prose is the best search representation;
- forgetting that users ask in a different vocabulary from the text they read;
- treating search-native artifacts as extra cleanup instead of a primary retrieval layer.

## Takeaways

- Query intent and author intent are not the same object.
- Search-native text can dramatically improve retrieval quality.
- The best retrieval system often searches a derived representation, not the raw passage alone.
