---
id: w3-06-negation-trap-scope-failures
title: "The Negation Trap and Scope Failures"
week: 3
topic: "Act II: A Field Guide to What Chunking Destroys"
order: 6
summary: Scope failures do not just lose information, they invert it, and presupposition accommodation silently promotes a hedged hypothesis to certainty with no error signal at all.
---

Scope failures deserve the most attention because they do not merely lose information — they **invert** it. Negation is the most dangerous culprit.

> "The meta-analysis found no significant evidence that Compound X increases cardiac risk in patients under 65. However, in patients 65–80 with hypertension, the data suggested a concerning elevation."

Surface only the second sentence and the reassurance-with-a-caveat becomes pure alarm; surface only the first and the caveat vanishes. Neither is the truth. The truth is the relation between them — and that relation lives exactly at the boundary where your chunker cuts.

## Where else scope breaks

The same trap springs on:

- **Conditional scope** — "If the debt-to-income ratio exceeds 43%, the following requirements apply…" Chunk away the condition and the requirements appear universal.
- **Counterfactual mood** — "Had the rate stayed at 3%, the portfolio would have appreciated 12%." The subjunctive that signals non-reality is the first casualty of a cut.
- **Epistemic hedging** — see presupposition accommodation below.

```python
# a toy demonstration: chunking a negated finding in half inverts its meaning
finding = (
    "The meta-analysis found no significant evidence that Compound X "
    "increases cardiac risk in patients under 65. However, in patients "
    "65-80 with hypertension, the data suggested a concerning elevation."
)

sentences = finding.split(". ")
chunk_a = sentences[0]      # "no significant evidence... under 65"
chunk_b = sentences[1]      # "...concerning elevation"

print("Chunk A alone reads as: reassurance")
print("Chunk B alone reads as: alarm")
print("Neither chunk carries the true, qualified relationship between them.")
```

## Presupposition accommodation

When a paper writes "we tentatively suggest, on preliminary evidence, that mechanism Y may play a role," the hedge scopes the whole claim. Three sentences later the authors use the shorthand of an established fact, as authors do. If the elaboration lands in a different chunk from the hedge, a tentative hypothesis is silently promoted to certainty. Epistemologists call this **presupposition accommodation**: encountering a claim without its epistemic frame, the reader (or retriever) treats it as shared background.

> This is the most insidious chunking failure — the one that produces no error signal at all. The system is confidently, silently wrong.

Negation, conditionals, counterfactuals, and hedges all share one property: the words that determine truth are far from the words that state the claim. A chunk boundary dropped between them doesn't blur the truth — it flips it.
