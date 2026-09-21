---
id: w10-01-place-memory-and-shared-context
title: "Place, Memory, and Shared Context"
week: 10
topic: "Act I: The Room as the Corpus"
order: 1
summary: "Some retrieval systems are about a document corpus; others are about a shared room of people, memory, and interaction."
---

## Core intuition

The context of a system is not always a flat file set. Sometimes the relevant memory is distributed across a shared environment: a room, a team, a process, or a set of user interactions.

## Why it matters

When a system is embedded in a collaborative context, retrieval must account for shared state, roles, recent actions, and social memory rather than just a static index.

## Instructor framing

This week reframes retrieval as a function of place and shared context, not only document similarity. The system must know what is “in the room” and what the participants are already assuming.

## Worked example

A team discussing a product launch has already agreed on budgets, milestones, and risk owners. A retrieval system that ignores that shared context may reintroduce stale assumptions or forgotten design constraints.

## Math explained step by step

The “score” in a shared context system is no longer just document-to-query similarity. It becomes a function of relevance, recency, co-ownership, and context compatibility.

## Practical pattern

In real systems, this often means maintaining:

- active project memory
- shared session state
- team-specific retrieval filters
- recent decisions and exceptions

## Common traps

- treating all context as equally fresh
- ignoring who shares the context
- retrieving from a global corpus without filtering for the active room or task

## Takeaways

- Context is local, social, and temporal as well as textual.
- Shared memory can be more important than raw retrieval quality.
- An assistant fitted to a room is often more useful than a generic one.
