---
id: w6-13-citation-faithfulness-and-guarding-the-guard
title: "Citation Faithfulness, Caught Hallucinations, and Who Guards the Guard"
week: 6
topic: "Act II: The Conscience — Keeping Bad Answers In"
order: 13
summary: A citation is itself a claim that can be false — and detecting a hallucination is worthless without a policy for what to do with it, which is where Act II confronts the recursive limits of its own machinery.
---

A grounded claim the user cannot check is only half honest — this is where citation enters, not as decoration but as the visible face of the conscience.

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
