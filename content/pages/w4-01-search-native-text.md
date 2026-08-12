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

This week we abandon that assumption, and the whole posture of the course shifts with it. We stop asking "how do I cut the document well?" and start asking a stranger, more powerful question:

> What if the best thing to search is text the document never literally said?

## The single thread to hold

A document is written for a reader — to be argued, defended, taught, or filed away. It is almost never written to be found by a short, blunt query typed into a search box. So before we index a document, we will manufacture new textual objects from it — **derivative artifacts** — each one written, this time, for the searcher. We will search those. And then, having found the right place, we will show the reader the original.

That last sentence is the entire week compressed:

> We search derived artifacts; we show original results.

## What this buys you, and what it costs

Every derivative artifact is a bet: pay a little extra computation and storage at ingestion time, in exchange for a much better chance that a real user's real query lands where it should. Act I spends its time making the case that this bet is necessary — that raw text actively resists search, by design, because of who it was written for. Act II builds the toolkit of artifacts and proves, on a real textbook, that the bet pays off. Act III lifts the same idea from a single passage to an entire corpus, culminating in RAPTOR.

Nothing in this week throws away last week's work. The raw-chunk index stays. We are giving it colleagues.
