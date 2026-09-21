---
id: w10-02-shared-memory-session-state
title: "Shared Memory and Session State"
week: 10
topic: "Act I: The Room as the Corpus"
order: 2
summary: "The memory of a system is not only eternal; it is also the state of the current room, the current task, and the current session."
---

## Core intuition

When a system is used by a team or a workflow, memory becomes shared state. The relevant context is not just what was said in the past, but what is currently active in the room.

## Why it matters

A team conversation is not a single user prompt. It carries assumptions, prior decisions, and unresolved trade-offs. Retrieval that ignores this state produces answers that sound smart but are disconnected from the current work.

## Instructor framing

This week redefines memory as a spatial and social object. The system must know whether the user is in the same project context, same session, same policy environment, or a different one.

## Worked example

A product team is discussing a launch plan. One member asks, "What is the financial risk if we push this by two weeks?" The answer must consider the current project decisions, budget assumptions, and stakeholder constraints already in the room, not just a generic risk summary from the global corpus.

## Math explained step by step

Shared context can be modeled as a context variable $C_t$ that changes over time and participants:

$$
R(q, C_t) = f(q, C_{t-1}, S_t, P_t)
$$

where $S_t$ is the session state and $P_t$ is the participant or role profile. The retrieval decision depends on more than a static document query; it depends on the active room.

## Practical pattern

Strong systems maintain a lightweight state object containing:

- current task or project ID
- recent decisions and unresolved questions
- user or team role
- prior retrieved evidence within the session

This makes the system more coherent across a single collaborative thread.

## Common traps

- treating a session as an unstructured log without explicit structure
- ignoring project boundaries and user context
- reading from a global index without the active room's state

## Takeaways

- Shared memory is operational memory.
- Session state is part of retrieval, not an optional wrapper.
- A room-aware assistant is more coordinated than a static one.
