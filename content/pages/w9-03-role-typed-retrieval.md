---
id: w9-03-role-typed-retrieval
title: "Role-Typed Retrieval and Tenant Isolation"
week: 9
topic: "Act I: Entitlement-Aware Retrieval and the Library of Many Catalogues"
order: 3
summary: "Users do not only differ by query. They differ by role, scope, and trust boundary, and the retrieval stack must respect that." 
---

## Core intuition

A retrieval system should know which roles are allowed to see which facts. Without that, the system can answer with the wrong scope even when the content is technically relevant.

## Why it matters

Tenant isolation, role-based access control, and office-level permissions are not metadata details. They are structural design constraints, because they change what can be retrieved at all.

## Instructor framing

This lesson forces the system to separate query relevance from user entitlement. Relevance answers "what matches the question?" Entitlement answers "what may this user access?"

## Worked example

A finance manager and a salesperson ask a similar question about pricing terms. The semantic content may overlap, but the answer space differs because the roles have different permission scopes. The retriever must understand the role before it selects the candidate set.

## Math explained step by step

The retrieval decision can be thought of as a constrained optimization over the user-role space:

$$
\max_{d \in D} S(q, d) \quad \text{subject to} \quad A_{role}(u, d) = 1
$$

This makes role and scope explicit in the search objective. The model can no longer treat the whole corpus as a shared common library.

## Practical pattern

In practice, teams usually maintain:

- scope tags for users and groups
- shard or index partitions by tenant or jurisdiction
- explicit access filters deep in the retrieval system
- role-aware answer validation before returning content

## Common traps

- using global retrieval even when the corpus is partitioned by tenant
- assuming the semantic layer automatically respects authorization
- neglecting cross-tenant contamination during indexing

## Takeaways

- A query is never independent of the caller's rights.
- Role-aware retrieval is a design requirement, not a UI decoration.
- Safety begins at the retrieval boundary.
