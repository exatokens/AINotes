---
id: w3-04-endophora-broken-references
title: "Endophora and Broken References"
week: 3
topic: "Act II: A Field Guide to What Chunking Destroys"
order: 4
summary: Language refers to itself through anaphora and cataphora, and cutting a chunk boundary between a pronoun and its antecedent leaves the fragment fluent but incoherent.
---

Act II is a field guide to failure. When a RAG system returns a confidently wrong answer, the root cause is rarely a bad embedding model or a poor prompt. More often it is a chunking decision made months earlier, silently severing a connection the system can never recover. Naming these pathologies gives you a diagnostic vocabulary — so that when your system fails, you can ask precisely which kind of failure it is.

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
