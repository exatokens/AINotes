---
id: a1-02-pot-of-milk-poc-to-production
title: "The Pot of Milk: Why POCs Never Reach Production"
week: 1
topic: "Act I: Why Agents, Why Now"
order: 2
summary: A folktale about a king's vessel of "milk" that turned out to be water explains why so many corporate agentic teams produce impressive demos that never survive contact with reality.
course: ai_agents
---

There's an old Indian folktale about King Akbar, who wanted to fill a giant vessel with milk to celebrate an occasion. He asked every courtier in the kingdom to bring one small pot of milk that evening and pour it in, unseen, under cover of night. Each courtier, alone in the dark, had the identical private thought: *everyone else is pouring in milk — surely my one pot of water will go unnoticed in this vast sea of white.* By morning, the vessel was full to the brim with perfectly clear water.

This is not a story about honesty. It's a story about how a team full of people each individually reasoning "someone else is doing the real work" produces a collective output with none of the real work in it at all. It maps disturbingly well onto how corporate GenAI initiatives actually get staffed, and it's worth sitting with before writing a single line of agent code, because it explains why the field is full of demos that dazzle in a conference room and evaporate the moment a real user — or a boss, or a client — actually pushes on them.

## Core intuition

A prototype's ease of construction is not evidence of its production-readiness. Modern agent-building tools have made the *first* 80% of an impressive-looking system trivially easy: write a prompt, wrap it in an orchestration framework, watch it produce plausible output on the examples you tried. That ease is exactly what makes teams stop there.

## Why it matters

The gap between "it works on my three test questions" and "it works reliably for ten thousand real users with weird edge cases" is not a small polish pass — it is most of the actual engineering. Teams that skip it produce systems that are "not repeatable, not deterministic, and not reliable," and the resulting reputational damage ("agents don't work") often falls on the technology rather than on the shortcut that was taken to build it.

## Instructor framing

Use the folktale as a diagnostic question you can ask of any team, including your own: who, specifically, on this team is bringing the milk — the deep technical rigor, the evaluation harness, the edge-case testing — and who is quietly assuming someone else already brought it? If the honest answer is "nobody," the vessel is full of water no matter how confident the block diagrams look.

## Worked example

The recap describes a common pattern: a company hires a VP of GenAI who is an excellent talker but not deeply technical. That VP hires directors and senior architects who are excellent at producing polished block diagrams and strategy decks. Those architects hire junior engineers who know the newest orchestration libraries and sound fluent in the vocabulary. Every layer of this hierarchy is individually plausible — good communicators, good diagram-makers, good library-users — and every layer is quietly hoping someone *else* in the stack is supplying the deep expertise. The junior engineers hope to learn from the "grandmaster" architects; the architects secretly hope the new hires already know what they're doing. The result is a team that ships a proof-of-concept that looks like an agent, demos like an agent, and buckles the first time it meets a query it wasn't specifically designed to handle — because nobody actually built the reliability machinery that separates a prototype from a product.

## Math explained step by step

The folktale is really describing a coordination failure, and it has a clean quantitative version worth internalizing, because it recurs later in this course as the logic behind gold-standard test sets and evaluation harnesses.

**Step 1 — model each contributor's private decision.** Suppose $n$ people each independently decide whether to contribute real rigor (probability $p$) or free-ride on the assumption that others will (probability $1-p$), and suppose each person's private belief is "the group's average contribution is already high, so my marginal contribution barely matters."

**Step 2 — see why uniform incentives produce a race to the bottom.** If everyone reasons this way simultaneously, the *expected* fraction of real contribution in the final pot is not $p$ for some comfortable middle value — it collapses toward $0$, because the reasoning that justifies free-riding is available to every single contributor at once, with no one able to observe anyone else's actual choice until it's too late (the pot is poured in the dark).

**Step 3 — see what breaks the collapse: observability.** The fix is not moral exhortation; it's removing the darkness. If each courtier's pot were poured in daylight, in front of everyone, free-riding would be instantly visible and the equilibrium changes completely. This is the exact same logic behind requiring a visible, shared gold-standard evaluation set later in this course (Week 3) — it converts an unobservable, diffusable responsibility ("is my agent good enough?") into a measured, attributable one.

**Step 4 — apply it to team structure.** A team with no shared, visible metric for "does this actually work" is structurally the King Akbar vessel: everyone's individual water looks like milk until someone actually tastes the batch.

## Practical pattern

1. Before staffing or joining an agentic project, identify who owns the "milk" — the deep technical rigor and the honest evaluation — explicitly, by name, not by assumption.
2. Build a small, visible measurement early (even a handful of real test cases with expected outputs) so that "does it work" stops being a private, diffusable judgment and becomes a shared, checkable one.
3. Treat "it worked in the demo" as a null result, not a positive one, until it has been checked against cases nobody hand-picked.
4. Resist hiring or building teams organized purely around vocabulary fluency (knowing the latest framework names) as a proxy for actual engineering depth.

## Common traps

- Mistaking a fluent, confident presentation of an agentic system for evidence that the system is reliable — fluency and reliability are produced by entirely different kinds of work.
- Assuming that because a system uses the newest orchestration framework, someone on the team has necessarily done the deep evaluation work — frameworks make first demos easy precisely because they don't require it.
- Organizational free-riding: every layer of a hierarchy assuming technical rigor exists at a different layer, with no layer actually owning it.
- Treating "reaching production" as a matter of scaling up an already-working prototype, rather than recognizing that most of the real engineering work hasn't started yet.

## Takeaways

- The pot-of-milk folktale is a precise metaphor for a coordination failure where individually rational free-riding collapses collective output to near-zero real contribution.
- Corporate GenAI teams frequently replicate this structure: technically fluent-sounding hierarchies where each layer assumes rigor exists elsewhere.
- The fix is the same fix as in the story — remove the darkness. Make quality measurable and visible early, rather than trusting a demo.
- This is the emotional and organizational preamble to the course's later insistence on gold-standard datasets and rigorous evaluation: those aren't bureaucratic overhead, they're the daylight that stops the pot from filling with water.
