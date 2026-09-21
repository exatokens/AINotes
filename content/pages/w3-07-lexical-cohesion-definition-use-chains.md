---
id: w3-07-lexical-cohesion-definition-use-chains
title: "Lexical Cohesion and Definition–Use Chains"
week: 3
topic: "Act II: A Field Guide to What Chunking Destroys"
order: 7
summary: Documents cohere through a sustained field of related words, and chunking dissolves that field, orphaning both disambiguating terms and legal definitions from their uses.
---

Documents also cohere through implicit connections. Halliday and Hasan identified five mechanisms of textual cohesion; the subtlest is **lexical cohesion** — the cumulative effect of related words that build a sustained semantic field, an *isotopy*. A legal brief that threads "negligence," "duty of care," "breach," "proximate cause," and "damages" across its pages makes each term resonate with the others. Chunk the brief and each fragment carries only a few of these terms; the field effect dissolves.

## Core intuition

A term is often not meaningful alone. Its meaning is built from the company it keeps across the document.

When chunking strips away that company, the term becomes ambiguous and brittle; the retriever sees a valid-looking word without the field that explains it.

## Why it matters

This is why smaller chunks can sometimes hurt retrieval quality. A single isolated term may be semantically less precise than a broader, context-rich passage in which the same concept is supported by its lexical neighbors.

## Instructor framing

The language of a document is not just a sequence of tokens. It is a field of recurring concepts. The chunk boundary is what breaks that field.

## Worked example


The word “breach” in a legal context carries meaning because it appears alongside “duty of care,” “proximate cause,” and “damages.” In a short isolated chunk, it could just mean a broken wall or a protocol violation. The lexical company changes the meaning.

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



## Math explained step by step

Read the `field_overlap` code above as a stand-in for what an embedding model is actually doing.

**Step 1 — treat a semantic field as a set of co-occurring terms.** `legal_field` is five terms that, appearing together, jointly signal "this is about tort law." No single term in the set carries that signal alone — "breach," "damages," and "duty" are each individually ambiguous or generic.

**Step 2 — measure how much of the field survives into each chunk.** `field_overlap` computes $|{\text{chunk terms}} \cap {\text{field}}| / |{\text{field}}|$: the full chunk keeps $2/5 = 0.4$ of the field's terms, the thin chunk keeps $1/5 = 0.2$. This is a toy proxy for what an embedding model does implicitly — the more field-members present, the more firmly the resulting vector is pulled toward the "legal tort" region of the space, because each additional co-occurring term is more corroborating evidence for the same neighborhood.

**Step 3 — see why the thin chunk's vector is genuinely more ambiguous, not just less informative.** With only "breach" present, the encoder has three live hypotheses (wall, protocol, whale) with no other words to disambiguate between them, so the resulting vector is a compromise — pulled partway toward all three senses, fully committed to none, similar to the "mixing principle" from two pages ago but caused by *missing* corroboration rather than *added* noise.

**Step 4 — connect this to the observed production effect.** As chunks shrink, the expected number of field-corroborating terms per chunk falls, so on average, embeddings drift toward more ambiguous, harder-to-rank regions of the space — which is precisely why smaller chunks can *reduce* retrieval quality despite being more "focused" on paper.

## Practical pattern

Chunking should preserve the local semantic field. Definitions, repeated terms, and domain phrases need their surrounding context to remain interpretable and retrievable. Concretely: when chunking domain-heavy text (legal, medical, technical), bias toward larger chunks or add a lightweight glossary/definition injection step — prepend a chunk's key defined terms with their definitions from elsewhere in the document — rather than trusting raw proximity to preserve the field.

## Common traps

- splitting the definition from its later uses — a term defined in §2.1 and used in §7.4 reaches the retriever looking like two unrelated generic words;
- indexing a term without its lexical neighborhood, especially for domain jargon that means something different outside the field (breach, discharge, consideration, execution);
- preferring mechanically small chunks over semantically coherent ones, on the unexamined assumption that "smaller and more focused" always improves precision;
- not noticing this failure mode at all, because nothing looks broken — the retrieved chunk contains the query term, and only a domain expert would spot that the surrounding field is missing.

## Takeaways

- Lexical cohesion is a major, easy-to-miss source of meaning: a term's disambiguation often comes from its neighbors, not itself.
- Definitions are only useful when attached to their later uses — an orphaned use of a defined term is functionally an undefined word to the retriever.
- Concretely: for domain-heavy documents, prefer chunks large enough to retain at least two or three field-corroborating terms, and consider explicitly re-injecting a term's definition wherever it is used far from where it was defined.
