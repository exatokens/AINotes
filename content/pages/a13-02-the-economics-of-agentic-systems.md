---
id: a13-02-the-economics-of-agentic-systems
title: "The Economics of Agentic Systems: Latency, Cost, and the Van Gogh Escalation"
week: 13
topic: "Act I: Coordinating Many Minds"
order: 2
summary: Frontier models incur sticker shock in an agentic loop for two compounding reasons — queued latency and multi-turn token consumption — and the fix is climbing the escalation ladder deliberately, painting a stick figure before attempting a Van Gogh.
course: ai_agents
---

A single frontier-model API call in isolation looks affordable. The same call, repeated across a genuinely agentic, multi-step workflow — planning, tool selection, observation, re-planning, dozens of times per task — produces a bill that surprises almost every team the first time they see it in production. This is not a pricing anomaly; it is the direct, compounding consequence of two structural properties of frontier-model usage that a single-call mental model hides completely. This page makes both properties explicit, and revisits the escalation ladder from Week 9 through a specifically economic lens: painting a stick figure before attempting a Van Gogh.

## Core intuition

Two forces compound to produce agentic sticker shock. **Latency**: a request to a frontier model does not execute in isolation — it enters a queue alongside millions of concurrent requests, traveling through massive shared data centers, producing per-call latency in the range of one to ten seconds for standard calls, and up to several minutes for "thinking" models performing extended reasoning. **Token consumption**: agentic reasoning is inherently multi-step and multi-turn — a system built entirely on frontier-model calls consumes far more tokens overall than a single-turn chatbot interaction would suggest, because every planning step, every tool-call decision, and every observation-processing step is itself a full model invocation with its own token cost.

The remedy is not "use a worse model" but decompose the problem well enough, through genuine planning, that most of the resulting sub-tasks do not require a frontier model at all — deferring to Local Models and Small Language Models (SLMs) wherever the specific sub-task's demands permit it.

## Why it matters

This reframes "which model should this agent use" from a single, system-wide decision into a per-sub-task decision made after decomposition, not before it. A system that routes every sub-task, however narrow, through the same frontier model pays both the latency tax and the token tax on every single step, compounding across a task that might require dozens of steps. A system that first decomposes the task (this week's earlier page's "one-trick pony" specialization, applied at the model-selection level too) and only escalates individual sub-tasks to a frontier model when their actual difficulty demands it can cut both latency and cost dramatically, without sacrificing overall task quality on the steps that genuinely need frontier-level reasoning.

## Instructor framing

Present the escalation ladder here not as a repeat of Week 9's version but as that same ladder read specifically for its *economic* consequences at each rung, using the Van Gogh metaphor to make the progression concrete rather than abstract: you do not create a masterpiece in one stroke. You begin with a rough first pass — a stick figure — at **Prompt Engineering**: coarse prompts, templates, basic chain-of-thought. If that's insufficient, you invest in **Prompt Optimization** (tools like DSPy, mathematically discovering better prompts) — layering in detail, correcting form, iteratively refining, the way a painter builds up a canvas rather than attempting the final image directly. Beyond that lie **Tools and Sidecars** (RAG, calculators, classifiers), then **Fine-Tuning**, then, for the hardest coordination problems, **Multi-Agent Reinforcement Learning** — the "Mount Everest" of the ladder, covered in the pages that follow.

## Worked example

Consider a customer-support agent handling a request that involves: detecting whether a message contains a social security number (a regex check), classifying the customer's intent (a task well within a small encoder model's competence), retrieving relevant account information (a database call, no model needed), and finally composing an empathetic, context-aware response (a task that genuinely benefits from a frontier model's language quality). A naive implementation routes all four steps through the frontier model, paying its latency and token cost four times over for a task where only the last step actually required that capability. A well-decomposed implementation runs the first three steps through free or near-free specialist components — a regex, a tiny classifier, a database lookup — and reserves the frontier-model call for the one step where its specific strength (nuanced, empathetic natural language generation) is actually load-bearing. The end-user-visible latency and the total token bill both drop substantially, with no loss in the quality of the step that mattered.

## Math explained step by step

Quantify the latency and cost compounding directly, to make "sticker shock" a computed, not merely anecdotal, consequence.

**Step 1 — model per-step latency.** For a task requiring $m$ sequential steps, each routed through a frontier model with per-call latency $\ell$ (say, 1–10 seconds for standard calls), naive total latency is roughly $m \cdot \ell$ — for $m = 20$ steps at $\ell = 3$ seconds average, total end-to-end latency is around 60 seconds, dominated entirely by queuing and network round-trips rather than any actual computation the task needed.

**Step 2 — model per-step token cost.** For the same $m$-step task, each frontier-model call processes not just the current step's new content but frequently a growing context of prior steps (recall Week 11's roughly 100:1 input-to-output ratio for agent loops) — total token cost scales at least linearly, and with a naive non-cached implementation, closer to quadratically, in $m$.

**Step 3 — compute the savings from selective decomposition.** Suppose only a fraction $f$ of the $m$ steps genuinely require frontier-model-level capability, and the remaining $(1-f)m$ steps can be routed to near-zero-latency, near-zero-cost specialist components (regex, small classifiers, direct API/database calls). Total latency drops from $m \cdot \ell$ to roughly $f \cdot m \cdot \ell$, and token cost drops proportionally — for $f = 0.25$ (only a quarter of steps genuinely need a frontier model), this is a fourfold reduction in both latency and cost, achieved purely through decomposition, without touching model quality on the steps where it matters.

**Step 4 — the design implication.** Because the achievable savings scale directly with how small $f$ can be made, the actual engineering leverage in agentic system economics lies overwhelmingly in *task decomposition quality*, not in negotiating better per-token pricing or squeezing marginal latency out of the frontier-model provider — the previous page's "one-trick pony" specialization argument and this page's economic argument are, quantitatively, the same lever pulled from two different angles.

## Practical pattern

1. before optimizing model choice or pricing at the system level, invest first in decomposing the task well enough to identify which sub-steps genuinely require frontier-level reasoning ($f$) versus which can be handled by cheap, fast specialists — this single decomposition step typically dominates all other cost and latency optimizations combined;
2. route deterministic or narrowly-scoped sub-tasks (pattern matching, classification, lookups) to regex, small classifiers, or direct API calls by default, reserving frontier-model calls specifically for steps requiring genuine language understanding, synthesis, or judgment;
3. treat the escalation ladder (prompt engineering → prompt optimization → tools/sidecars → fine-tuning → MARL) as an economically justified sequence, not a purely capability-justified one — each rung both increases achievable quality and changes the CapEx/OpEx trade-off, echoing Week 9's Pareto-frontier material directly;
4. measure $m$, $\ell$, and $f$ for your own system empirically before assuming a specific optimization (caching, smaller models, fewer steps) will help — the compounding math above shows where the actual leverage sits, but the exact numbers are system-specific.

## Common traps

- routing every sub-task in an agentic workflow through the same frontier model out of implementation convenience, paying both a latency and a token-cost tax on steps that never needed frontier-level capability;
- treating agentic cost overruns as a pricing problem to be solved by provider negotiation or model downgrades, when the actual leverage lies in task decomposition quality ($f$ in the derivation above);
- underestimating how much latency comes from queuing and network overhead rather than actual computation, and consequently under-investing in reducing the *number* of frontier-model calls per task rather than trying to make each individual call faster;
- skipping the earlier rungs of the escalation ladder (prompt engineering, prompt optimization) and reaching directly for fine-tuning or multi-agent RL to solve a cost or latency problem that better decomposition and cheaper specialist components would have solved more directly.

## Takeaways

- Agentic systems incur cost and latency sticker shock from two compounding structural forces: per-call queuing latency (roughly 1–10 seconds per frontier-model call) and multi-turn token consumption that scales with task length.
- The primary lever for controlling both is task decomposition quality — routing only the fraction of steps that genuinely require frontier-model capability through one, and handling the rest with cheap, fast, narrow specialist components.
- The escalation ladder, read economically, is a sequence of increasingly capable but increasingly expensive rungs, each changing the underlying CapEx/OpEx trade-off from Week 9's Pareto-frontier framing — climb only as far as the specific sub-task actually requires.
- The Van Gogh metaphor captures the right mental model directly: build up agentic capability in layers — a rough first pass, then systematic refinement — rather than expecting a single frontier-model call to paint the masterpiece in one stroke.
