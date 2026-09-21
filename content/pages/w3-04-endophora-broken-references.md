---
id: w3-04-endophora-broken-references
title: "Endophora and Broken References"
week: 3
topic: "Act II: A Field Guide to What Chunking Destroys"
order: 4
summary: Language refers to itself through anaphora and cataphora, and cutting a chunk boundary between a pronoun and its antecedent leaves the fragment fluent but incoherent.
---

Act II is a field guide to failure. When a RAG system returns a confidently wrong answer, the root cause is rarely a bad embedding model or a poor prompt. More often it is a chunking decision made months earlier, silently severing a connection the system can never recover. Naming these pathologies gives you a diagnostic vocabulary — so that when your system fails, you can ask precisely which kind of failure it is.

## Core intuition

A document is not a bag of independent sentences. It is a network of references, and those references are often the very thing the answer depends on.

When a chunk boundary cuts between a pronoun and its antecedent, the fragment may still read like English while losing the meaning it requires.

## Why it matters

This is why chunking failures can look like model failures. The generator is not hallucinating from nowhere; it is being asked to answer from pieces that have been stripped of the context needed for resolution.

## Instructor framing

This chapter begins the field guide to chunking pathologies. The book is teaching you to diagnose failures at the level of discourse, not just at the level of model quality.

## Worked example


The sentence “It was rather pleased with itself” becomes meaningless when the antecedent “the cow” is in another chunk. The text remains grammatical, yet the semantic connection is gone.

## Anaphora and cataphora

Language refers to itself. "The cow jumped over the moon. It was rather pleased with itself." The pronoun "it" points backward to "cow" — this is **anaphora**. Cut the two sentences into different chunks and the second becomes incoherent. The mirror image is **cataphora**, a forward reference: "He had no money. Yet John hoped to eat anyway." Both are forms of **endophora** — text referring to other text in the same document — and both saturate technical and legal writing. "As we saw in Equation 3.6…" is meaningless if Equation 3.6 sits three chapters away in another chunk.

```python
# a sentence-boundary chunker -- clean cuts, but blind to what they sever
import re

def sentence_chunk(text):
    return re.split(r'(?<=[.!?])\s+', text.strip())

text = "The cow jumped over the moon. It was rather pleased with itself."
chunks = sentence_chunk(text)
print(chunks)
# ['The cow jumped over the moon.', 'It was rather pleased with itself.']
# the second chunk, embedded alone, has lost its antecedent -- "it" refers to nothing
```

## The purity–amnesia trade-off, in miniature

This is the purity–amnesia trade-off you will see again and again this week: small chunks trade purity for amnesia. A fifty-token chunk likely holds one thought, but may lack the context to resolve its pronouns and abbreviations. In Indian philosophy all meaning is said to live in one syllable — Om — but that is meaning compressed by millennia of shared context, which no embedding model possesses.

> In practice, meaning without context is noise.

Endophora is the simplest pathology to name and the easiest to demonstrate — but it is only the first entry in the field guide. Discourse structure, negation, lexical cohesion, and bridging inference each sever a different kind of thread.



## Math explained step by step

Look at what the sentence-boundary chunker's output actually costs you, step by step.

**Step 1 — the chunker's rule is purely syntactic.** `re.split(r'(?<=[.!?])\s+', text)` looks only for punctuation. It has no model of what a pronoun refers to; "It" and "cow" are, to this code, two unrelated tokens in two unrelated strings.

**Step 2 — embed each resulting chunk independently.** The encoder sees `"It was rather pleased with itself."` with zero visibility into the previous sentence. Whatever vector it produces has to represent "it" as some generic, referent-less pronoun — the encoder cannot invent the missing antecedent.

**Step 3 — compare that to what the embedding would have captured intact.** Embedded together, "the cow...it" resolves the coreference the way a human reader does, and the resulting vector sits meaningfully near "cow" and "satisfaction." Embedded apart, the second vector sits in a generic, low-information region of the space — grammatically fine, semantically adrift.

**Step 4 — see why no downstream fix recovers this.** A re-ranker or LLM reading the orphaned chunk in isolation faces the same missing information the encoder did; it can only guess or hedge, since the antecedent was never encoded into that chunk's vector at all. The loss happened at chunk time, and nothing after chunk time can see what was severed.

## Practical pattern

A good chunking strategy must preserve local discourse relations: pronouns, references, definitions, and argument frames. If a chunk cannot stand alone without its antecedent or its context, it is not a safe retrieval unit. Concretely: run a coreference resolver (or a cheap heuristic — never let a chunk boundary fall between a pronoun-initial sentence and the sentence before it) before finalizing chunk boundaries, and prefer overlapping windows over hard cuts wherever pronoun density is high.

## Common traps

- assuming sentence boundaries are semantic boundaries — a clean regex split is not a safe chunk boundary;
- letting pronouns or abbreviations float at the start of a chunk with no antecedent inside that same chunk;
- failing to preserve referential context in retrieval units, especially in technical writing full of "the above," "as noted," and "this approach";
- trusting that a fluent-sounding fragment is a complete one — fluency and coherence are not the same test.

## Takeaways

- Endophora is a core chunking failure mode: a grammatically complete sentence can still be semantically empty once separated from its antecedent.
- A self-contained sentence can still be semantically incomplete — check for pronouns and cross-references before treating a sentence as chunk-safe.
- Concretely: never let a chunk start with a pronoun, demonstrative ("this," "that," "the above"), or cross-reference whose antecedent lives in a different chunk — merge it backward or run coreference resolution first.
