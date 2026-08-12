---
id: w3-07-lexical-cohesion-definition-use-chains
title: "Lexical Cohesion and Definition–Use Chains"
week: 3
topic: "Act II: A Field Guide to What Chunking Destroys"
order: 7
summary: Documents cohere through a sustained field of related words, and chunking dissolves that field, orphaning both disambiguating terms and legal definitions from their uses.
---

Documents also cohere through implicit connections. Halliday and Hasan identified five mechanisms of textual cohesion; the subtlest is **lexical cohesion** — the cumulative effect of related words that build a sustained semantic field, an *isotopy*. A legal brief that threads "negligence," "duty of care," "breach," "proximate cause," and "damages" across its pages makes each term resonate with the others. Chunk the brief and each fragment carries only a few of these terms; the field effect dissolves.

## Why this matters geometrically

A chunk holding "breach" *and* "proximate cause" embeds firmly in legal territory. A chunk holding "breach" alone could mean a breached wall, a breach of protocol, or a whale breaching the surface. The isotopy disambiguates; chunking destroys it; retrieval suffers.

> This explains a genuinely puzzling production observation: retrieval quality sometimes degrades as chunks get smaller, even though smaller chunks should be more focused. The focused chunk has lost its lexical company.

## Definition–use chains

Definition–use chains are the same wound in sharper form. A contract defines "Covered Losses" once, in §2.1; thereafter every use carries that definition's weight. Chunk the document and a §7.4 passage about "Covered Losses" reaches the retriever orphaned from its definition — two generic English words where a precise legal term was meant. The same pattern haunts API docs, medical acronyms, and standards documents: one definition, many uses, and chunking preserves the uses while severing the source.

```python
# illustrating the isotopy effect: a term's disambiguating company disappears
# when a chunk holds only a fragment of the semantic field
legal_field = {"negligence", "duty of care", "breach", "proximate cause", "damages"}

chunk_full = {"breach", "proximate cause"}     # embeds firmly in legal territory
chunk_thin = {"breach"}                         # could be a wall, a protocol, a whale

def field_overlap(chunk_terms, field):
    return len(chunk_terms & field) / len(field)

print("full chunk field coverage:", field_overlap(chunk_full, legal_field))
print("thin chunk field coverage:", field_overlap(chunk_thin, legal_field))
# the thin chunk's lone term is ambiguous without its lexical company
```

Lexical cohesion is invisible in a way endophora is not — there is no broken pronoun to point to, just a term stripped of the company that used to disambiguate it. It is one more way a "focused" chunk can be worse off than a broader one.
