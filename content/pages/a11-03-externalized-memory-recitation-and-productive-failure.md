---
id: a11-03-externalized-memory-recitation-and-productive-failure
title: "Externalized Memory, Recitation, and Productive Failure"
week: 11
topic: "Act I: Inside Manus"
order: 3
summary: Long-running agents fight three problems no context window fixes on its own — running out of room, forgetting the goal, and losing the evidence of their own mistakes — and the filesystem, a recited todo list, and an intact error trace solve all three.
course: ai_agents
---

An agent fifty tool calls into a task is a very different creature from an agent on its first call. It has accumulated a long, sprawling history of actions and observations, some of them enormous (a scraped web page, a full PDF's text), and it is one goal-drift away from quietly working on the wrong sub-problem. Modern context windows of 128K tokens and beyond make this feel like a solved problem, but in practice it is often a liability rather than a comfort: model performance measurably degrades well before the technical context limit is reached, long inputs stay expensive even with caching, and a single oversized observation can consume the entire budget in one step.

This page works through three techniques — used across production agent systems, Manus prominent among them — that solve this not by fighting for more context, but by being disciplined about what stays *in* context at all: pushing bulk state out to a filesystem, deliberately re-writing the goal back into the model's recent attention, and — counterintuitively — refusing to clean up the record of the agent's own mistakes.

## Core intuition

**The filesystem as context.** Rather than truncating or summarizing an agent's growing history — an inherently lossy operation, since you cannot reliably predict which observation from ten steps ago will turn out to matter — treat the file system as the agent's real long-term memory: unlimited in size, persistent, and directly operable by the model itself. Compression then becomes *restorable* rather than destructive: a web page's content can be dropped from context as long as its URL is preserved; a document's contents can be omitted as long as its path in the sandbox remains available. Nothing is permanently lost — it is simply not resident in the expensive, limited window right now.

**Recitation.** Long agent loops drift, because a goal stated once at the very start of a fifty-step context is progressively pushed further from the model's most-attended region — the well-documented "lost in the middle" phenomenon. The fix used by Manus is deceptively simple: maintain a `todo.md` file and rewrite it, updated and checked off, at each step. This recites the objective into the *end* of the context every time, keeping the global plan in the model's most recent attention span without any architectural change to the model itself — pure context engineering, manipulating attention through natural language repetition rather than through any special mechanism.

**Keeping failures in context.** The instinctive response to an agent error is to clean the trace, retry silently, and reset state. This is a mistake: erasing a failure erases the evidence the model would otherwise use to update its own behavior. Leaving a failed action and its resulting error observation *in* context lets the model implicitly shift its own prior away from repeating that action — error recovery, treated this way, becomes one of the clearest behavioral markers of a genuinely agentic system, and one still underrepresented in benchmarks that only measure success under ideal conditions.

## Why it matters

All three techniques share a structural insight: an agent's *effective* memory is not bounded by its context window so much as by what it chooses to keep resident there, and naive strategies for managing that residency — truncate the old, hide the errors, trust the model to remember the goal — actively destroy the information the agent needs most. A team that truncates aggressively to save tokens routinely finds their agent re-doing work it already did, because the evidence it needed was thrown away. A team that hides failures from the model finds it repeating the identical mistake indefinitely, because nothing in the model's input ever signaled that the mistake had occurred.

## Instructor framing

Connect all three techniques back to the earlier Manus page's KV-cache discipline: filesystem offloading, recitation, and preserved failure traces must all still respect append-only, prefix-stable context management, or the memory-preservation benefit is bought at the cost of a broken cache. A `todo.md` rewritten at every step, for instance, is *not* edited in place inside the model's context — it is appended as a fresh event each time, keeping the history append-only while still achieving the recitation effect.

## Worked example

A resume-screening agent asked to review twenty candidates is a clean illustration of why *not* cleaning up context can misfire in the opposite direction — the "don't get few-shotted" pattern, closely related to keeping failures in but distinct from it. If the agent's context is full of near-identical past action-observation pairs (open resume, extract fields, score, repeat), the model, an excellent mimic of patterns in its own context, tends to fall into a rhythm and repeats the same action shape even when a specific resume calls for a different approach — leading to drift or hallucination on the outliers. The fix is deliberate structured variation: different serialization templates, alternate phrasing, minor noise in ordering — enough diversity to break the rut without discarding any actual information. This is the fourth discipline alongside filesystem-offloading, recitation, and preserved failures: keep information, but don't let its *presentation* become so uniform that the model starts pattern-matching the shape of the context instead of reasoning about the current task.

## Math explained step by step

Quantify the "lost in the middle" attention-decay problem that recitation is designed to counteract.

**Step 1 — model attention decay with position.** Empirically, a transformer's effective attention to a token at relative position $j$ tokens back from the current generation point decays roughly monotonically for large $j$ — approximate this crudely as an attention weight $w(j) \propto 1/(1 + \alpha j)$ for some decay constant $\alpha > 0$ (a simplification, but sufficient to illustrate the mechanism).

**Step 2 — see the goal statement's fate without recitation.** If the goal is stated once at position $0$ and the agent is now at step $n$ with roughly $r$ tokens of accumulated context per step (recall the roughly 100:1 read-to-write ratio from the KV-cache page), the goal sits at effective distance $j \approx r \cdot n$ — for $n = 50$ and $r = 100$, $j \approx 5000$, deep enough into the "lost in the middle" region that $w(j)$ may be small relative to the freshly-appended, highly-attended tokens at the end of context.

**Step 3 — see recitation's effect.** By rewriting the plan (including the original goal, restated) at the *end* of context every step, recitation effectively resets $j \to 0$ for the goal statement at every single iteration, regardless of how large $n$ grows — the goal is always at the highest-attention position, no matter how long the task has run.

**Step 4 — the practical corollary.** Because this reset is purely a function of *where in context* the goal is restated, not of context length or model architecture, it is a technique that costs a small, constant number of extra tokens per step (rewriting a todo list) in exchange for eliminating an attention-decay failure mode that would otherwise scale directly with task length — making it disproportionately valuable exactly on the longest, highest-value tasks.

## Practical pattern

1. treat any large, bulky observation (a scraped page, a document, a big API response) as a candidate for filesystem offloading the moment it's captured — keep only a restorable pointer (URL, file path) in the live context, and design your own tool wrappers to do this automatically rather than relying on the model to remember to do it;
2. build a recitation mechanism into any agent expected to run more than a handful of steps — a periodically rewritten, appended plan/todo artifact costs little and directly counters attention decay on the original goal;
3. never silently swallow or clean up a failed action's error trace before it reaches the model's next context — preserve it, exactly as it occurred, so the model has the evidence needed to avoid repeating the mistake;
4. audit your context for repetitive, near-identical action-observation patterns on tasks involving many similar sub-items (batch processing, review queues) and deliberately introduce structured variation in serialization or phrasing to prevent the model from pattern-matching form over substance.

## Common traps

- aggressively summarizing or truncating context to save tokens without first checking whether the discarded information is restorable — irreversible compression risks losing exactly the detail that turns out to matter ten steps later;
- resetting or hiding a failed action's trace "to keep things clean," which removes the only signal the model has that the action failed and needs a different approach next time;
- assuming a large context window (128K+ tokens) makes goal-drift a non-issue, when attention decay with position is an empirical phenomenon independent of the technical context limit;
- letting repetitive batch-style tasks produce a uniformly-patterned context, inadvertently causing the model to imitate the shape of its own recent actions rather than reason freshly about each new item.

## Takeaways

- Treat the filesystem, not the context window, as an agent's real long-term memory — offload bulk state with a restorable pointer rather than compressing it away irreversibly.
- Recitation — periodically rewriting the goal and plan into the most recently attended part of context — counteracts attention decay ("lost in the middle") at a small, constant token cost per step, and its value scales with task length.
- Preserve failed actions and their error traces in context rather than cleaning them up; erasing evidence of a mistake removes the model's only signal to avoid repeating it.
- Watch for context that has become too uniform in a batch-style task — deliberate structured variation prevents the model from falling into an unhelpful pattern-matching rut.
