---
id: w9-02-permission-as-a-retrieval-constraint
title: "Permission as a Retrieval Constraint"
week: 9
topic: "Act I: Entitlement-Aware Retrieval and the Library of Many Catalogues"
order: 2
summary: "A retrieval system must treat permission as a first-class constraint, not a downstream check."
---

## Core intuition

The document set is not just semantically relevant; it is also policy-relevant. A retriever that ignores access boundaries is not merely incomplete; it is unsafe.

## Why it matters

If permission is considered only after retrieval, the system can leak sensitive context into the model or the answer. In production, the retrieval layer is often the first enforcement point.

## Instructor framing

This is the operational version of the earlier claim that retrieval is not only sequence similarity. It is permission-aware selection under constraints.

## Worked example

A support analyst asks for all known incidents involving a regulated customer. If the retriever considers all records equally and filters only after generation, the answer could expose another tenant's contract terms. A permission-aware pipeline excludes that candidate set before ranking begins.

## Math explained step by step

The candidate set is constrained by an authorization predicate $A(u, d)$:

$$
R(q, u) = \{d \in D : S(q, d) > \theta \land A(u, d) = 1\}
$$

where $S(q, d)$ is the relevance score and $A(u, d)$ is whether the user is entitled to see the document. This makes authorization part of the retrieval problem itself, not a patch applied later.

## Practical pattern

Best practice is to combine:

- access metadata on the document or chunk
- user identity and tenant context
- pre-filtering before semantic scoring
- verification of the final answer against the same policy boundary

## Common traps

- filtering after the fact
- assuming that a good semantic match is also a safe one
- forgetting that the retrieval layer can become the leakage channel

## Takeaways

- Security is a retrieval question.
- Access control is part of the information architecture.
- The correct system filters before it reasons.
