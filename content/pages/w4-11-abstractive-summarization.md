---
id: w4-11-abstractive-summarization
title: "Abstractive Summarization: Trading Detail for Altitude"
week: 4
topic: "Act III: Altitude — Summaries, RAPTOR, and the Corpus"
order: 11
summary: A summary is not a compression but a change of altitude, trading fine detail for large-scale structure and answering the thematic queries no single chunk can.
---

Everything in Act II was local. Factoids, rewrites, and QA pairs operate at the altitude of a single passage. But some questions cannot be answered from any one passage, however well we extract it — because their answer is not *in* the document; it is *about* the document. For those we must gain altitude.

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
