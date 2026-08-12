---
id: w4-05-factoids
title: "Factoids: Distilling the Atoms of Meaning"
week: 4
topic: "Act II: The Derivative Artifacts — and the Proof"
order: 5
summary: A factoid is the smallest textual unit that still means something, the semantic molecule left after you pry every self-contained claim loose from a paragraph.
---

Act II builds a toolkit of derivative artifacts. The first, and the most atomic, is the **factoid**.

> A factoid is the smallest textual unit that still means something.

The chemistry analogy is more than decorative: a molecule is the smallest unit that retains the properties of a substance. Split water and you get hydrogen and oxygen — useful, but no longer wet. A factoid is the semantic molecule: split it and you have fragments that are no longer about anything.

## Finding the factoids hiding in a paragraph

Consider a paragraph from a geography text:

> Berlin, situated on the banks of the River Spree, serves as the capital of Germany and is its most populous city, with a metropolitan population exceeding six million residents. The city has been a center of European politics since reunification in 1990.

This single paragraph hides at least five factoids:

1. Berlin sits on the Spree.
2. Berlin is the capital of Germany.
3. Berlin is Germany's most populous city.
4. Berlin's metropolitan population exceeds six million.
5. Berlin has been a political center since 1990.

Each is a complete, standalone claim — and not one of them appears in the paragraph as an isolated sentence. The phrase "the capital of Germany" is welded into a longer clause. **Extraction** is the act of prying it loose and making it self-contained, resolving the pronouns and implicit references so the factoid can stand alone in the index with no memory of its paragraph.

## The craft is in the self-containment

A lazy extractor returns "It is the capital" — useless, because "it" has been severed from "Berlin." A good extractor returns "Berlin is the capital of Germany."

This is why factoid extraction is the part of the pipeline that rewards prompt optimization most: the difference between a self-contained factoid and a dangling fragment is the difference between a retrievable thought and noise. In production, the prompts used for this step are typically the product of heavy DSPy-driven tuning over the target corpus — this is not a place to accept the first prompt that seems to work.

```python
# the shape of a factoid-extraction call — the prompt quality is the whole game
def extract_factoids(chunk_text, llm_fn):
    prompt = f"""Decompose the following passage into self-contained factoids.
Each factoid must be a complete claim that resolves every pronoun and
implicit reference (no "it", "this", "the city" without its name).

Passage:
{chunk_text}

Return one factoid per line."""
    return llm_fn(prompt).splitlines()
```

Once extracted, each factoid is indexed on its own — no longer diluted by four neighbouring claims — and a pointed query walks straight up to the one vertex that matters.
