---
id: w11-02-caching-for-common-queries
title: "Caching for Common Queries"
week: 11
topic: "Act I: Cachecraft, Shareability, and the Searchable Commons"
order: 2
summary: "Repeated retrieval work should not always be recomputed; good caching is a system design decision, not an optimization afterthought."
---

## Core intuition

The same semantically identical or near-identical queries recur. When they do, the system should reuse earlier work rather than re-running the whole pipeline from scratch.

## Why it matters

As the system scales, repeated retrieval and answer synthesis become costly. Shared reuse is the difference between an expensive prototype and a sustainable product.

## Instructor framing

This week widens the lens from the single request to the system as a shared commons. The retrieval system is part of a social and infrastructural environment, not a pure personal assistant.

## Worked example

A policy bot sees the same question about refund eligibility repeated across a set of users. The expensive work is not in the final answer generation alone; it includes fetch, rerank, and evidence assembly. A cache that stores the high-value candidate set or the final answer under policy constraints can reduce cost dramatically.

## Math explained step by step

The decision to reuse or recompute can be framed as a trade-off:

$$
\text{Benefit of Cache} = \text{Recompute Cost} - \text{Freshness Risk} - \text{Staleness Penalty}
$$

If a query is common, stable, and low-risk, a cache provides huge savings. If it changes frequently, freshness dominates and recomputation may be preferable.

## Practical pattern

Practical systems distinguish between:

- exact answer caching
- retrieval result caching
- semantic/embedding query caching
- freshness policies and invalidation rules

This keeps reuse effective without violating correctness standards.

## Common traps

- caching too aggressively and serving stale results
- caching only the final answer while ignoring the retrieval bundle
- treating every repeated query as identical when the user context differs

## Takeaways

- Reuse is a design feature, not a minor optimization.
- Good caching respects freshness and policy.
- Searchable commons scale when trust is built into the cache layer.
