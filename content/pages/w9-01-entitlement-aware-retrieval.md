---
id: w9-01-entitlement-aware-retrieval
title: "Entitlement-Aware Retrieval"
week: 9
topic: "Act I: Entitlement-Aware Retrieval and the Library of Many Catalogues"
order: 1
summary: "Not every user should see every document; the retrieval layer must respect permission, role, and access boundaries."
---

## Core intuition

Retrieval is not just semantic similarity; it is also policy-aware access. A document can be relevant and still be forbidden.

## Why it matters

The most dangerous retrieval failure is not a wrong answer. It is an answer that reveals information the user should not have access to.

## Instructor framing

This week shifts the system design from pure retrieval quality to trust boundaries. The right answer must be both relevant and authorized.

## Worked example

A support agent asks for customer records. The system may retrieve a document that is highly relevant but belongs to a different tenant, region, or permission class. The retrieval system must respect the boundary before passing evidence to the model.

## Math explained step by step

The retrieval problem becomes a constrained search: among all relevant documents, only those meeting the current access policy and user entitlement should be candidates. Relevance and authorization are separate filters, and the system must treat them as such.

## Practical pattern

Strong systems usually include:

- user and tenant policy tagging
- document-level or section-level access metadata
- pre-filtering before semantic retrieval
- compliance checks on final response generation

## Common traps

- retrieving first and filtering too late
- assuming semantic relevance implies policy permission
- forgetting that access control is part of the retrieval contract

## Takeaways

- Policy-aware retrieval is a trust requirement, not an optional feature.
- Access control and semantic relevance are separate dimensions.
- A safe answer is a relevant answer that is also properly authorized.
