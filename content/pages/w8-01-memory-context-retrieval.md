---
id: w8-01-memory-context-retrieval
title: "Memory, Context, and Retrieval"
week: 8
topic: "Act I: Memory, Context, and Retrieval"
order: 1
summary: "The system's memory is not just a database; it is the context layer that decides which facts are worth reusing and which are just noise."
---

## Core intuition

A model needs memory to be selective, not merely large. The difference between a helpful assistant and a noisy one is whether it can recall what matters and ignore what does not.

## Why it matters

Context windows, memory systems, and retrieval policies determine whether a model behaves like a disciplined assistant or a confused summarizer.

## Instructor framing

This week turns the course toward a different axis: not just retrieving candidate facts, but deciding what context should be held in memory at the right moment.

## Worked example

Suppose a user asks about a contract dispute from three months ago. A naive assistant may answer from a stale summary or irrelevant conversation context. A stronger system resolves the right memory source, attaches the right temporal scope, and keeps only the most relevant facts in context.

## Math explained step by step

Memory is a selection problem. At any given time, the system must decide which evidence to keep, which to compress, and which to drop. Retrieval becomes a policy problem: how much context is enough for a reliable decision?

## Practical pattern

Operationally, memory systems often separate:

- long-term corpus storage
- recent conversation memory
- dynamic retrieval over active task context
- summarization of older but still relevant facts

This division prevents context from being either too sparse or too noisy.

## Common traps

- keeping too much context and drowning the model in irrelevant detail
- forgetting that time and provenance matter
- treating memory as a flat log instead of a structured retrieval system

## Takeaways

- Memory is not just storage; it is active selection.
- Retrieval quality depends on context discipline as much as chunk quality.
- A reliable system remembers the right facts at the right time.
