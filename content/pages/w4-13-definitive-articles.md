---
id: w4-13-definitive-articles
title: "From One Book to a Library: RAPTOR's Definitive Articles"
week: 4
topic: "Act III: Altitude — Summaries, RAPTOR, and the Corpus"
order: 13
summary: Run RAPTOR over a corpus rather than a document and its upper nodes stop summarizing one source, instead synthesizing a canonical answer across every document that touches the topic.
---

Run RAPTOR over a single document and its upper nodes are summaries of that document. But run it over a corpus — a hundred papers, a thousand support tickets, every internal memo on a topic — and the clusters no longer respect document boundaries. A cluster gathers the chunks that are about the same thing, drawn from wherever they live. Its summary is therefore something new: not a digest of any one source, but a **synthesis across all of them** — a definitive article on a topic that no single document contains.

## The PRML-and-ESL example

Imagine asking a shelf — PRML and Hastie–Tibshirani–Friedman's *Elements of Statistical Learning* together — "what is overfitting?" A naive system returns Bishop's best chunk or ESL's best chunk. A corpus-level RAPTOR node returns one coherent answer that has already reconciled both treatments into a single, canonical paragraph.

That is the **definitive-article property**, and it is the reason this technique is not merely "summarization with extra steps."

> Philip Anderson's "More Is Different" names the principle exactly: at each level of scale, qualitatively new properties appear that are invisible at the level below. A document's theme is an emergent property of its chunks — present in none of them, visible only from altitude. The corpus-level article is the same idea one level up: it exists in none of the source documents and could not, because it is a property of the collection, not of any member.

## Where this leaves off, on purpose

To build that corpus-level article well, you eventually want to cluster not by raw embedding proximity but by relational structure — which entities and ideas are genuinely connected across documents. That is community detection over a graph: network analysis, modularity, the Leiden algorithm, the move "from local to global." It deserves its own day.

Notice, though, that you have already met its seed twice this week: once in RAPTOR's soft clustering of a corpus, and once in the observation that a corpus has a structure no single document can see. Next week the seed becomes a forest — GraphRAG, and its memory-augmented cousin — where "find the communities, then summarize each one" is the same instinct as today's, scaled from one document's paragraphs to a whole corpus's ideas.

## The whole week, in one breath

> Text is written for a reader. Search needs an artifact written for the query. So we manufacture those artifacts, we search them — alongside the raw chunks, never instead of them — and we show the reader the original. We retrieve the derivative. We generate from the source.
