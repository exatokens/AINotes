---
id: w4-08-passage-rewrites
title: "Passage Rewrites: The Source's Understudy"
week: 4
topic: "Act II: The Derivative Artifacts — and the Proof"
order: 8
summary: A passage rewrite reformulates a hostile span into plain search-friendly language while the original clause remains the only thing ever shown to the reader or cited to the model.
---

Not all text is written to be found. Academic prose is written to be argued, legal prose to be defended, corporate prose to be forgotten.

> A passage rewrite reformulates a span in plain, direct, search-friendly language — without changing its meaning.

We keep the original; the rewrite is a shadow document, indexed alongside it, invisible to the user but highly visible to the retriever.

## Example: a legal clause

Original:

> Notwithstanding the provisions of Section 12(b), the Licensor retains the irrevocable right to terminate this Agreement upon thirty (30) calendar days' written notice.

Search-friendly rewrite:

> The licensor can terminate the agreement with 30 days' written notice, regardless of Section 12(b).

The rewrite embeds closer to how a user would ask — "can the licensor end the agreement early?" — yet the original clause, with all its operative force, remains the authoritative passage handed to the generation model.

> This is the understudy who auditions for the retriever so that the star can take the stage to perform.

## The risk, and how it is defused

The rewrite carries a real risk: simplification can shed precision. "Irrevocable" is a legal term of art the plain rewrite drops. The risk is defused by the core pattern (the next page): the rewrite only *finds* the clause; the original is what the generator reads and cites. The rewrite is the bait; the original is the evidence.

## HyDE: the mirror image

QA pairs (next page) make the index question-shaped at ingestion time. **HyDE** does the opposite: it makes the *query* document-shaped at query time — it asks an LLM to hallucinate a hypothetical answer, embeds that, and retrieves against it. Both close the same genre gap from opposite ends, and you can do both at once.
