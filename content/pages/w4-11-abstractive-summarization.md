---
id: w4-11-abstractive-summarization
title: "Abstractive Summarization: Trading Detail for Altitude"
week: 4
topic: "Act III: Altitude — Summaries, RAPTOR, and the Corpus"
order: 11
summary: A summary is not a compression but a change of altitude, trading fine detail for large-scale structure and answering the thematic queries no single chunk can.
---

Everything in Act II was local. Factoids, rewrites, and QA pairs operate at the altitude of a single passage. But some questions cannot be answered from any one passage, however well we extract it — because their answer is not *in* the document; it is *about* the document. For those we must gain altitude.

## Core intuition

Some questions require a summary, not a fact. When the answer is a theme, a trend, or a narrative across many paragraphs, the retrieval target must live at a higher level of abstraction.

## Why it matters

This is the bridge from local retrieval to global understanding. Summaries are not redundant with factoids; they are a different class of retrieval object for a different class of question.

## Instructor framing

Hold the balloon metaphor hard: students will want to treat a summary as "a shorter version of the same information," which invites the dangerous assumption that a good-enough summary can substitute for the source. Make the point explicitly that altitude change is a *different kind of object*, not a lossy copy of the same kind — a coastline's shape and a single house's floor plan are both true, and neither is a compressed version of the other.

## Worked example

A 40-page quarterly report contains, buried across sections, a revenue table (Section 3), a churn analysis (Section 5), and a competitive-landscape discussion (Section 7). Ask "how is the business doing overall?" and no single section answers it — the honest answer synthesizes all three. A per-document summary written to answer exactly this altitude of question might read: "Revenue grew 8% year-over-year despite a 3-point rise in churn, largely offset by share gains against the two largest competitors." That sentence exists nowhere verbatim in the report — Bishop-style, it is distributed across three sections — and no factoid extraction, however thorough, would ever produce it, because factoids preserve ground-level precision, not cross-section synthesis. Only a summary manufactured specifically to answer "what's the state of the business" can serve that query.



The system has to answer both the narrow question and the broad question. Factoids answer one; summaries answer the other. The book treats them as complementary, not competing.

## Compression is the wrong metaphor

> A summary is not a compression. It is a change of altitude.

"Compression" suggests the same content packed tighter into a smaller box. Summarization is not that. It is ascent in a balloon: you rise, and large structures invisible from the ground swim into view — the shape of the coastline, the pattern of the fields — while the fine details that filled your vision on the ground vanish. You trade resolution for scope. Neither view is truer. They are different altitudes over the same land.

This is why summaries are the complement of factoids, never their replacement. **Factoids sacrifice context for precision; summaries sacrifice precision for context.** Some queries are unanswerable from the ground: "what is this report about?", "what are the main findings?", "how does this policy differ from the last version?" No single chunk contains the answer, because the answer is distributed across the whole. Only a summary — an artifact manufactured to live at altitude — can be retrieved in response.

## Three engineering decisions

1. **Granularity** — summarize per chunk, per section, per document, or per corpus. Each is a different artifact with different retrieval behaviour.
2. **Faithfulness** — an abstractive summary can hallucinate, and for RAG a confident false summary is worse than none. Faithfulness must be enforced by prompting, verification, or citation requirements.
3. **Indexing** — summaries usually live in their own namespace, because their retrieval characteristics are too different from chunks to blend.

## Summaries at many granularities

| Granularity | Answers |
|---|---|
| Per section | "what does the methods section cover?" |
| Per document | "what is this paper's contribution?" |
| Per corpus | "what is this whole collection about?" |

Each is cheap to generate relative to its value, and each catches a band of thematic queries the others miss. The instinct of the week — one source, many representations — applies along the altitude axis just as it did along the precision axis in Act II.

Once you have summaries at several fixed altitudes, you are one small step from making altitude *continuous*. That step is RAPTOR.






## Math explained step by step

Formalize "altitude, not compression" as a claim about what a summary's embedding is even meant to be near.

**Step 1 — a chunk embedding is meant to be near queries about that chunk's specific content.** A factoid about churn is meant to be the nearest vector to a query asking specifically about churn — precision is the design goal, and irrelevant neighboring content is treated as noise to be excluded (recall the dilution inequality).

**Step 2 — a summary embedding is meant to be near queries about the *relationship between* multiple pieces of content.** "Revenue grew 8% despite rising churn, offset by competitive share gains" is not "about" any one topic more than another — its embedding sits somewhere that reflects the *co-occurrence and interaction* of three themes, a location that has no counterpart among the leaf-level chunks at all, because none of them individually discusses the interaction.

**Step 3 — see why this is not the same optimization problem as dilution, even though both involve averaging-like effects.** Dilution (Week 4, earlier pages) is a failure: a chunk's embedding is a mixture of *unrelated* claims, which hurts retrieval because no query wants the mixture. A summary's embedding is a deliberate synthesis of *related* claims, built specifically because some queries want exactly that synthesis. Averaging is harmful when claims are unrelated and the query wants one of them; averaging (of a more sophisticated, LLM-mediated kind) is the entire product when claims are related and the query wants their relationship.

**Step 4 — see why granularity is therefore a retrieval-target design decision, not a compression-ratio decision.** Choosing "summarize per section" versus "summarize per document" is choosing which set of queries you're building a retrieval target for — a finer granularity serves narrower synthesis questions ("what does the methods section conclude"), a coarser one serves broader questions ("what is this paper's contribution") — exactly analogous to choosing chunk size in Week 3, but one level up the altitude axis.

## Practical pattern

Building a summarization layer into a retrieval index:

1. generate summaries at 2-3 fixed granularities (section, document, and optionally corpus) rather than just one — each answers a genuinely different band of thematic query, mirroring the table above;
2. store summaries in a separate index namespace from raw chunks and factoids — their retrieval statistics (typical similarity ranges, appropriate top-$k$) differ enough from ground-level artifacts that blending them can distort ranking;
3. enforce faithfulness explicitly: require the summarization prompt to cite which source sections informed each claim, and spot-check a sample against the source before trusting the pipeline — an abstractive summary that hallucinates a plausible-sounding synthesis is worse than no summary, because it is indistinguishable in fluency from an accurate one;
4. route thematic-sounding queries ("what is this about," "summarize the findings," "how does X compare to Y") toward the summary index specifically, either via query classification or by always including summary-index results alongside chunk-index results in the candidate pool.

## Common traps

- treating a summary as a lossy compression that could, in principle, be reconstructed into the original — this framing invites using summaries as source material, which risks laundering a hallucination into the answer;
- indexing summaries in the same namespace as chunks and factoids without accounting for their different similarity distributions, causing top-k to skew toward one artifact type for reasons unrelated to relevance;
- generating only one granularity of summary and expecting it to serve all thematic queries — a document-level summary is too coarse for "what does section 3 argue" and too fine for "what does this whole corpus cover";
- failing to enforce or verify faithfulness, and discovering only downstream that a summary asserted a synthesis the source material does not actually support.

## Takeaways

- A summary is a different kind of retrieval object from a chunk or factoid — built to answer synthesis and thematic queries no single passage can, not a compressed version of ground-level detail.
- Averaging content is harmful when claims are unrelated (dilution) and constructive when claims are related and a query wants their relationship (summarization) — the same mathematical operation, opposite verdicts, depending on what the query needs.
- Concretely: generate summaries at multiple explicit granularities (section, document, corpus), store them separately from chunk-level indexes, and enforce faithfulness checks before trusting an abstractive summary as retrievable evidence.
