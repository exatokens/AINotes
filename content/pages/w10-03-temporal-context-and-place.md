---
id: w10-03-temporal-context-and-place
title: "Temporal Context and Place"
week: 10
topic: "Act I: The Room as the Corpus"
order: 3
summary: "The same document has different meanings depending on when it is retrieved and in what room it is being used."
---

## Core intuition

Context is local in both time and place. A fact may be valid in one project phase but stale in another. A retrieval system must understand when and where the fact belongs.

## Why it matters

If a system ignores temporal and situational context, it will produce answers that are technically true but operationally wrong. This is a failure of relevance, not just correctness.

## Instructor framing

This is the move from static knowledge to situated knowledge. Good systems treat time, venue, and team commitments as part of the retrieval state.

## Worked example

A product team asks, "Are we still constrained by the previous launch budget?" The answer depends on whether that budget was already revised, whether the question arrives during a planning session, and whether the team is in the launch room or the earlier exploration room.

## Math explained step by step

A fact's value depends on context and recency:

$$
V(d | q, t, r) = f(\text{relevance}, \text{freshness}, \text{room-compatibility})
$$

where $t$ is time and $r$ is the active room or project context. This makes retrieval a function of situated conditions, not only the query alone.

## Practical pattern

Teams often model this with:

- timestamps and validity windows
- project or workspace identifiers
- task phases and checkpoint states
- a preference for current-room facts over global historical facts

## Common traps

- ignoring recency when the data is time-sensitive
- mixing contexts from different teams or projects
- assuming a higher-ranked fact is always the correct fact for this room

## Takeaways

- Place and time are part of retrieval semantics.
- The best answer is often the one that fits the current room and moment.
- Good memory systems are situational, not universal.
