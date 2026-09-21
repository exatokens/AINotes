---
id: w6-13-citation-faithfulness-and-guarding-the-guard
title: "Citation Faithfulness, Caught Hallucinations, and Who Guards the Guard"
week: 6
topic: "Act II: The Conscience — Keeping Bad Answers In"
order: 13
summary: A citation is itself a claim that can be false — and detecting a hallucination is worthless without a policy for what to do with it, which is where Act II confronts the recursive limits of its own machinery.
---

A grounded claim the user cannot check is only half honest — this is where citation enters, not as decoration but as the visible face of the conscience.

## Core intuition

A citation is a second-order claim: it asserts that the referenced passage supports the sentence. If the citation is wrong, the answer looks grounded while being unverifiable.

## Why it matters

This is the final guardrail at the answer boundary. A system can be faithful to its context and still lie about where that faithfulness came from.

## Instructor framing

"Who guards the guard" is the philosophical high point of the week, and the temptation is to treat it as an unanswerable koan. Push past that: the actual answer the page gives ("verification is easier than generation, so each layer is more reliable than what it checks, even without certainty") is a real, load-bearing engineering principle, not a shrug — make sure students can state it as a positive claim, not just repeat the Latin.

## Worked example



Suppose an answer states: "Return processing takes 5-7 business days [Passage 2]." Checking Passage 2 directly reveals it actually discusses shipping times, not returns — the real supporting text, about returns taking 5-7 business days, sits in Passage 4, which the model never cited. The claim itself is perfectly true and grounded somewhere in the retrieved evidence; the citation attached to it is simply false. A user who trusts the footnote and goes to verify will find Passage 2 says nothing about returns, conclude (wrongly) that the whole answer is fabricated, and lose trust in a system that was actually right — a citation error that costs credibility even when the underlying claim was sound. Now consider the more dangerous mirror case: an answer states "the CEO previously worked at a competitor [Passage 1]," and Passage 1 is a real, existing, on-topic document — it just never mentions the CEO's prior employer at all. Here the citation looks completely legitimate (a real passage, plausibly on-topic) while doing nothing to actually support the claim it's attached to — the footnote lent its credibility to a fact it never verified.

We now audit not just the answer but the provenance chain of each sentence. The footnote is part of the evidence graph, not an ornament.

## Does the footnote hold?

When an answer says "the deadline is April 15 [3]," the marker is a promise: passage three supports this sentence, go and see for yourself. Citation is the system voluntarily handing the user the curtain-cord — the anti-Oz gesture made literal. But a citation is itself a claim, and it can be false in a way distinct from everything else: a model can produce a sentence perfectly grounded in passage $e_5$ while citing $e_2$ — the claim is faithful, the citation is a lie. Or, more insidiously, it can nail a real-looking citation to a fabricated claim, borrowing the credibility of the footnote to launder the hallucination.

The **ALCE** benchmark made citation quality automatically measurable along two axes:

| Axis | Question |
|---|---|
| **Citation recall** | Does every sentence that needs support carry a citation whose passages entail it? Are there uncited claims that should be cited? |
| **Citation precision** | Are the citations present actually relevant — does the cited passage really support the sentence, or was the footnote padding? |

The two form the same precision-recall tension seen at every layer this week: a system can carpet-bomb every sentence with every passage identifier (perfect recall, terrible precision) or cite sparingly and accurately (the reverse). Both axes are computed, at bottom, by the same NLI entailment check from the bipartite graph — citation faithfulness is that graph read through a different lens: does the edge the answer *asserts* (its footnote) match an edge the verifier *finds* (real entailment)?

> Oz never cited a source; his authority was pure projection. A system that makes falsifiable claims about its own evidence is, by construction, not a humbug — which is why citation verification is a core organ of conscience, not a cosmetic afterthought.

## What to do with a caught hallucination

Detection is worthless without disposition. The bipartite graph hands you a labeled set of claims — grounded, contradicted, ungrounded. The grounded ones survive and carry their citations. For the rest, four moves, in rough order of ambition:

| Move | When it's right |
|---|---|
| **Regenerate** — send the answer back with offending claims named, or run the self-healing loop (retrieve fresh evidence targeted at the ungrounded claim) | best first move for an **extrinsic** hallucination, where the claim might be supportable if the right passage is fetched |
| **Drop** — excise the ungrounded sentence, keep the rest | the default under strict grounding; correct for a **fabrication** no retrieval will ever ground |
| **Hedge** — keep the claim but mark its epistemic status ("the sources do not directly confirm this, but…") | appropriate for augmented-knowledge products where the user has consented to parametric contribution, provided provenance is marked |
| **Refuse** — decline and hand over the sources for the user's own review | when too much of the answer is ungrounded and the stakes are high |

> Disposition follows strictness. The same caught hallucination has different correct dispositions under different products: strict grounding (legal, medical) drops or refuses; augmented knowledge hedges; a research assistant may keep-and-mark. The detector is universal; the remedy is a product decision.

## Who guards the guard?

Here is the beautiful, uncomfortable recursion at the bottom of the Act: every verifier is itself a model. The NLI checker has its own error rate; the LLM judge has its documented biases; the semantic-entropy detector met in Act III can be confidently wrong about its own confidence. We built the response-side conscience to catch the generator's hallucinations — but the conscience can hallucinate too.

*Quis custodiet ipsos custodes?* Who guards the guard? There is no verifier at the bottom of the stack that is certainly correct. What there is, instead, is the same asymmetry that made the whole enterprise viable — **verification is easier than generation** — so each layer of checking, though imperfect, is more reliable than the layer it checks.

> We do not achieve certainty. We achieve a tower of successively more trustworthy approximations, and, crucially, we make our uncertainty auditable rather than hidden.

So do not oversell what has been built here: a response-side grounding stack does not make a RAG system truthful — it makes it **accountable**. It cannot guarantee that no hallucination ever reaches a user; it can guarantee that most do not, that the ones that do are the subtle residue rather than gross fabrications, and — this is the part that matters — that the system carries the machinery to say "I am not sure" instead of booming with borrowed confidence. Sometimes the honest response is no response at all, which is where Act III picks up.






## Math explained step by step

Formalize citation precision and recall as a direct reuse of the bipartite graph, then formalize the "who guards the guard" resolution as a statement about relative, not absolute, reliability.

**Step 1 — express citation recall in graph terms.** For each claim $c_i$ that the graph already marked grounded (some $e_j$ entails it), citation recall asks: does the answer's *own* footnote for $c_i$ point at an $e_j$ with a real entailment edge? If claim $c_i$ is grounded by $e_4$ but cited as $[2]$, recall fails for that claim even though the underlying fact is fine — recall is measuring "is every true grounding relationship also disclosed," not "is every claim true."

**Step 2 — express citation precision the mirror way.** For each *citation* the answer actually makes (footnote $[j]$ attached to claim $c_i$), precision asks: does the edge $(c_i, e_j)$ the answer asserts match a real entailment edge the verifier finds? A citation pointing at a real, on-topic, but non-entailing passage fails precision even though nothing about the citation looks obviously wrong.

**Step 3 — see why both checks reuse the identical NLI machinery from the bipartite graph, just applied to a different pair.** Faithfulness asks "does *some* $e_j$ entail $c_i$?" (existential over all evidence). Citation precision asks "does *this specific* $e_j$ — the one cited — entail $c_i$?" (a single, targeted entailment check). No new verifier needs to be built; citation checking is the same entailment function, called with the answer's own claimed edge as the pair to test, rather than searched for.

**Step 4 — formalize "verification is easier than generation" as a claim about relative error rates, not absolute correctness.** Let $\epsilon_{\text{gen}}$ be the generator's hallucination rate and $\epsilon_{\text{verify}}$ be the verifier's error rate (missing a real hallucination, or flagging a true claim). The entire tower of checks (NLI, then LLM judge, then a human audit sample) is viable specifically because each successive layer's $\epsilon$ is smaller than the layer below it's effective error rate *after* the layer above already caught most of the easy cases — not because any single $\epsilon$ reaches zero. This is why the recursion terminates in practice (a finite, affordable stack of imperfect checks) rather than requiring an infinite regress of "who checks the checker."

## Practical pattern

Building citation verification and hallucination disposition into a production pipeline:

1. compute citation precision and recall using the same NLI verifier already built for the bipartite graph — treat this as a near-free extension of existing machinery, not a separate system to build and maintain;
2. define your disposition policy (regenerate / drop / hedge / refuse) explicitly per product tier before deployment, using the strictness table as a template — a legal or medical product should default to drop-or-refuse, an internal research tool may default to hedge, and this decision should be made deliberately, not left as emergent model behavior;
3. log every caught hallucination's disposition as an auditable event, including which verifier caught it and at what confidence — this audit trail is what makes the "accountable, not truthful" framing operational rather than aspirational;
4. budget for periodic human review of a random sample of grounded (not just flagged) answers — since every verifier in the stack can itself be wrong, the only way to catch a systematic verifier blind spot is a check that doesn't depend on the same verification machinery.

## Common traps

- treating citation accuracy as automatically implied by content faithfulness — a claim can be perfectly true and grounded while citing the wrong passage, or a citation can point at a real, relevant-looking passage that doesn't actually support the claim;
- building a separate citation-checking system from scratch instead of reusing the existing NLI entailment machinery with the answer's own claimed citation as the pair to test;
- picking one disposition policy (e.g., always regenerate) for every caught hallucination regardless of type — an extrinsic hallucination often can be fixed by targeted re-retrieval, but a fabrication (invented entity, invented statute) will not be fixed by retrieving again, since there is nothing real to find;
- treating "we have a verifier" as equivalent to "our answers are truthful" — the verifier reduces and localizes error, and makes it auditable, but does not eliminate it, and marketing or product framing that implies otherwise sets an expectation the architecture cannot meet.

## Takeaways

- A citation is a second-order claim that can be false independently of the claim it's attached to — checking citation precision and recall reuses the same NLI entailment machinery as the faithfulness graph, applied to the answer's own asserted claim-to-evidence link.
- Detecting a hallucination is worthless without a disposition policy (regenerate, drop, hedge, refuse), and the right disposition depends on both the hallucination type (extrinsic vs. fabrication) and the product's required strictness — this is a product decision, not something the detector determines on its own.
- Concretely: every verifier in the stack is itself fallible, so the honest engineering target is a system that makes its uncertainty auditable and its errors the subtle residue rather than gross fabrications — not a system that claims to have eliminated hallucination entirely.
