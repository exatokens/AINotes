---
id: w8-03-episodic-vs-semantic-memory
title: "Episodic Memory and Semantic Memory"
week: 8
topic: "Act I: Memory, Context, and Retrieval"
order: 3
summary: "A useful assistant needs both remembered events and stable facts; the difference between them determines how memory should be retrieved."
---

## Core intuition

There are at least two kinds of memory relevant to a reasoning system: the memory of events and the memory of facts. A model that treats them as the same thing will confuse recency, ownership, and meaning.

## Why it matters

Users often ask for both kinds of memory at once: "What happened in our last conversation?" and "What is the contract standard for this situation?" Different memory types need different retrieval strategies.

## Instructor framing

Episodic memory is about sequences and events. Semantic memory is about abstract concepts and reusable patterns. A system that only stores the latter will forget the flow of a task; a system that only stores the former will fail to generalize.

## Worked example

A user says, "Last week we agreed to keep vendor risk below a threshold. What was the decision we made for the pilot launch?" This is episodic memory: it depends on the sequence of earlier steps. Another question, "What is the general policy for escalation when a vendor misses a SLA?" is semantic memory: it depends on the stable policy and not the exact timeline.

## Math explained step by step

We can separate the memory state into:

$$M = M_{episodic} \cup M_{semantic}$$

where episodic memory tracks events, time, and causality, while semantic memory stores stable abstractions and canonical facts. Retrieval should be conditioned on the type of question:

- event-based queries should favor episodic memory
- conceptual queries should favor semantic memory
- mixed queries should combine both, weighted by recency and relevance

## Practical pattern

A practical memory architecture uses different stores:

- recent conversation history as episodic memory
- canonical FAQs or policies as semantic memory
- retrieval policies that weight recency for event queries
- grounding rules that prefer stable facts when the user is asking a general question

## Common traps

- flattening all prior interactions into one bag of text
- mixing policy facts and personal history without provenance
- treating a recent conversation detail as if it were a general principle

## Takeaways

- The system needs both event memory and fact memory.
- Retrieval should adapt to the kind of memory the question is asking for.
- Memory quality is not just about volume; it is about separation of concern.
