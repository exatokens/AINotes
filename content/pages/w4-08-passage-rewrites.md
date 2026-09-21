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

## Core intuition

A document can be authoritative and still be a poor retrieval object. Rewriting the same facts into the user's language gives the retriever a second, query-shaped handle without altering what the model should cite.

## Why it matters

The rewrite is a retrieval aid, not a source of truth. It improves discoverability while preserving the original as the evidentiary authority.

## Instructor framing

The "understudy" metaphor is doing real pedagogical work — make students say back what an understudy actually does in a theater: rehearses and performs the audition/rehearsal role, but never takes the actual stage on opening night. A passage rewrite auditions for the retriever; it never appears in front of the generator or the user. If a student proposes showing the rewrite to the end user "since it's clearer," that is the exact failure this page is warning against.

## Worked example



This is the first example of a dual-index design: the retriever sees a reformulated version, the generator reads the authoritative original. The whole system becomes more robust because the retrieval artifact and the evidence artifact are different objects.

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






## Math explained step by step

Quantify why the rewrite scores higher without claiming the original scores badly in some absolute sense.

**Step 1 — decompose similarity into a "content" component and a "register" component.** Two texts about the same fact, written in different registers (legalese vs. plain speech), share content but diverge in register — vocabulary, sentence structure, hedging conventions. An embedding model responds to both, so $\cos(q, d)$ for a plain-language query against legalese is suppressed by the register mismatch even when content overlap is total.

**Step 2 — see the rewrite as a register transformation that holds content fixed.** "Notwithstanding the provisions of Section 12(b), the Licensor retains the irrevocable right to terminate..." and "The licensor can terminate the agreement with 30 days' written notice..." assert the identical fact — the rewrite's entire job is to change *only* the register term, moving it from legal formality toward the plain-question register a user query is drawn from.

**Step 3 — verify the query benefits specifically from the register match, not from any new information.** "Can the licensor end the agreement early?" shares almost the rewrite's exact register (short, plain, declarative-adjacent) — so $\cos(q, \text{rewrite})$ is high largely *because* the register term in the decomposition is near-zero distance, not because the rewrite added facts the original lacked.

**Step 4 — see precisely why the original must still be what's cited.** The rewrite optimized register at the cost of precision — "irrevocable" carries legal weight ("cannot be revoked or challenged later") that "can terminate" does not preserve. The similarity gain in Steps 1-3 is a retrieval-time gain only; nothing in the rewrite's construction guarantees its precision is sufficient for the generation step, which is exactly why the core pattern (next page) never lets the rewrite be the thing quoted.

## Practical pattern

Building a passage-rewrite pipeline:

1. write rewrite prompts that explicitly preserve every operative term (obligations, conditions, exceptions, defined terms) even while simplifying sentence structure — the risk is losing "irrevocable," not losing fluency;
2. never surface the rewrite to the end user or the generator — store it purely as a second, retrieval-only index entry with a pointer back to the source passage;
3. spot-check a sample of rewrites against their originals for dropped legal, medical, or technical qualifiers before trusting the pipeline at scale — this is the same "read the artifacts, not just the metrics" discipline QA-pair generation requires;
4. pair passage rewrites with HyDE when query-side transformation is cheaper than ingestion-side generation for your corpus — both close the same gap, from opposite ends, and using both is not redundant.

## Common traps

- showing the rewrite to the user or feeding it to the generator as if it were the source — this defeats the entire purpose of keeping the original as the evidentiary authority;
- writing rewrite prompts that optimize purely for plain-language fluency, silently dropping precise legal or technical qualifiers ("irrevocable," "notwithstanding," dosage units) in the process;
- assuming a higher retrieval score for the rewrite means the rewrite is a more accurate document — it means the rewrite's register is closer to the query's register, which is a retrieval property, not a truth property;
- treating the rewrite as a one-time artifact that never needs re-auditing — if the source document is amended, the rewrite must be regenerated, or it will confidently point retrieval at now-stale language.

## Takeaways

- A passage rewrite trades precision for register-match, which is exactly why it must never be the thing shown to the user or cited by the generator.
- The similarity gain from a rewrite comes from closing the register gap (legalese vs. plain speech), not from adding new information the original lacked.
- Concretely: always store rewrites with a pointer back to the source and route only the source to generation — treat the rewrite purely as a retrieval-time lure, never as evidence.
