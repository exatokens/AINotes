---
id: w3-06-negation-trap-scope-failures
title: "The Negation Trap and Scope Failures"
week: 3
topic: "Act II: A Field Guide to What Chunking Destroys"
order: 6
summary: Scope failures do not just lose information, they invert it, and presupposition accommodation silently promotes a hedged hypothesis to certainty with no error signal at all.
---

Scope failures deserve the most attention because they do not merely lose information — they **invert** it. Negation is the most dangerous culprit.

## Core intuition

Negation and hedging are not local punctuation marks. They are operators that change the truth of the whole claim by a specific scope.

When a chunk boundary cuts across the scope, the system may retrieve a fragment whose wording sounds authoritative but whose meaning is inverted or overstated.

## Why it matters

This failure can transform “no evidence of harm” into “clear evidence of harm,” or a tentative suggestion into a confident fact. In a high-stakes setting, that is more than an annoyance — it is an integrity problem.

## Instructor framing

This chapter makes the danger very concrete: chunking is not only a retrieval problem, but a semantic truth-preservation problem. Scope is part of the meaning.

## Worked example


A sentence such as “There is no significant evidence that compound X increases risk in patients under 65” is meaningful only when read with the precise scope of the condition. Isolate it and you remove the qualifiers; isolate the later caveat and you get an alarmist fragment that is not the whole story.

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



## Math explained step by step

Use the two-chunk code example to see exactly where the inversion happens, and why embeddings cannot repair it after the fact.

**Step 1 — embeddings encode local sentiment and topic, not cross-sentence logical scope.** Chunk A, "no significant evidence that Compound X increases cardiac risk," embeds with mildly reassuring, low-risk semantics — the encoder reads "no," "no significant," and the topic words, and lands somewhere calm.

**Step 2 — Chunk B is embedded with zero knowledge that Chunk A exists.** "In patients 65-80 with hypertension, the data suggested a concerning elevation" embeds with alarmed, elevated-risk semantics. Nothing in Chunk B's vector encodes that it is a *narrower, age-restricted* addendum to Chunk A's broader finding — the age restriction and the relationship between the two clauses is exactly the information chunking discarded.

**Step 3 — see why retrieval then serves whichever framing the query resembles more.** A query like "is Compound X safe" resembles Chunk A's calm language and retrieves it alone — silently dropping the caveat. A query like "does Compound X increase cardiac risk" resembles Chunk B's alarm language and retrieves it alone — silently dropping the "no significant evidence... under 65" scope that would have contextualized it as an *age-specific* finding, not a universal one.

**Step 4 — quantify why this produces no error signal.** Both retrievals return high-similarity, on-topic, fluent, individually-true text. There is no similarity threshold, no confidence score, no perplexity spike that flags "this fragment, while accurate on its own, states the opposite emphasis of the source when read alone" — which is exactly why this is, as the page says, the pathology that produces zero error signal.

## Practical pattern

When the evidence includes negation, conditionals, or uncertainty, retrieval units must preserve the full scope. The framing clause and the claim clause must travel together or the answer becomes structurally distorted. Concretely: flag sentences containing negation ("no," "not," "no significant"), conditionals ("if," "unless," "provided that"), or hedges ("suggests," "preliminary," "may") during chunking, and force the sentence immediately before and after to stay in the same chunk rather than splitting on a plain sentence boundary.

## Common traps

- splitting a negated statement from the population or condition it applies to, letting the negation appear to generalize beyond its actual scope;
- losing conditional or counterfactual qualifiers ("if," "had," "would have") when a chunk boundary falls right after them;
- promoting tentative findings into facts by omission — dropping "tentatively," "preliminary," or "may" when the elaborating sentence lands in a different chunk than the hedge;
- assuming that because a retrieved fragment is factually accurate in isolation, it is safe to present as the answer — accuracy-in-isolation and faithfulness-to-the-source are different properties.

## Takeaways

- Scope determines truth, not isolated wording — the same sentence can support opposite conclusions depending on what it's compared against.
- Negation, conditional, and hedging failures can invert or overstate the meaning of a retrieval result with no error signal at all.
- Concretely: treat any sentence containing "no," "not," "unless," "if," "may," or "preliminary" as chunk-glue to its neighboring sentence — never split immediately before or after one.
