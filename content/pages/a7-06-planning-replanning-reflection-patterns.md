---
id: a7-06-planning-replanning-reflection-patterns
title: "Beyond ReAct: Planning, Re-Planning, and Reflection"
week: 7
topic: "Act III: Designing Agents That Plan, Fail, and Reflect"
order: 6
summary: A bare ReAct loop errors out when it hits max_retries with no recovery path — planning, re-planning, and reflection are three design patterns that add resilience by letting an agent revise its own plan or judge its own output quality.
course: ai_agents
---

A plain ReAct loop — reason, act, observe, repeat — is the default starting point for most agent implementations, and it works well until it doesn't. The failure mode is specific and unglamorous: the agent tries an action, it fails, it tries again, it fails again, and after some fixed number of attempts it hits a `max_retries` limit and the whole process simply errors out. No recovery, no adaptation, just a stop.

This is a design gap, not an inherent limitation of agentic reasoning, and the course introduces three patterns that close it, each addressing a different way an agent's initial approach can go wrong: the plan itself is bad, execution of an otherwise-fine plan repeatedly fails, or the output quality is poor even though nothing technically errored. Three problems, three patterns, and they compose.

## Core intuition

**Planning and execution**: instead of jumping straight into acting, the agent first calls the LLM with a dedicated prompt to produce a step-by-step plan, which then guides a separate execution phase (often a ReAct-style loop). This separates "decide what to do" from "do it," and produces more robust behavior than mixing planning and acting together implicitly on every step.

**Re-planning**: when execution hits a failure — the ReAct agent exhausts its retries and would otherwise simply error out — a re-planning node catches this and triggers a fresh call to the planner, now informed by the context of what just failed, producing a new plan rather than halting. This turns a dead end into a recoverable state.

**Reflection**: the agent examines its own past steps and their results, judging whether the output actually meets quality criteria (correctness, completeness, alignment with stated user preferences) rather than assuming any output that didn't technically error is good enough. If the self-assessment is negative, the agent loops back for a better attempt — the same cyclical shape as re-planning, but triggered by quality judgment rather than execution failure.

## Why it matters

These three patterns address genuinely different failure modes, and conflating them leads to using the wrong recovery mechanism for a given problem. A ReAct agent that gets stuck in an infinite loop or hits `max_retries` has an *execution* problem — the plan (implicit or explicit) it's following isn't working in practice, and re-planning with the new context of what failed is the right response, not reflection, because there's no output yet to judge the quality of. A reasoning agent that produces a technically successful, non-erroring output that nonetheless fails to meet the user's actual needs has a *quality* problem — nothing crashed, so re-planning triggered by an execution failure wouldn't even fire, and reflection is the mechanism that catches this instead, by explicitly asking the model to assess its own work against criteria rather than assuming success-without-error equals success.

Planning-and-execution, meanwhile, is a preventive pattern rather than a recovery pattern — it reduces how often the other two failure modes occur in the first place, by making sure the agent has a coherent multi-step plan before acting rather than improvising step-by-step with no larger structure, the same distinction from earlier in the course between a "true agentic system" and a "workflow with a touch of AI."

## Instructor framing

Use the smart-home reasoning project as the connective tissue across all three patterns, since it's rich enough to motivate each one separately rather than needing three disconnected examples. Introduce the base if/then/else smart-home system first, show why it fails on nuanced cases (the Sophie-the-dog example), then layer in planning-and-execution, re-planning, and reflection one at a time against the same running scenario, so students see each pattern solving a specific, concrete gap in the previous version rather than encountering three abstract design patterns with no shared throughline.

## Worked example

The smart-home alerting system starts as rigid if-then-else logic: `IF back_door_open THEN send_alert`. This fails on nuanced, context-dependent cases — the user wants an alert if their dog Sophie seems stressed, but explicitly does *not* want an alert just because the back door is open while the main gate is closed, since that's a known-safe pattern (dog on the porch, perimeter secure). No amount of additional if/else branches comfortably captures every such nuance, which is exactly the motivation for a reasoning-based agent instead.

Layer in planning-and-execution: given the current sensor state, the agent first calls an LLM to produce a plan — "check gate status; check Sophie's stress indicators; check time of day; decide whether combined signals warrant an alert" — rather than jumping straight to a decision. Layer in re-planning: if the plan's execution phase fails (say, a sensor API call errors out repeatedly), instead of the whole reasoning process crashing at `max_retries`, a re-planning node catches the failure and asks the planner to produce a new plan aware of the sensor's unavailability — perhaps falling back to a more conservative default given incomplete information, rather than erroring out entirely. Layer in reflection: after producing a decision, the agent reviews its own reasoning against the user's stated preferences — "did I correctly weigh the gate-closed exception the user described?" — and if the self-assessment finds it didn't, loops back for a corrected judgment before finalizing the alert decision.

## Math explained step by step

Model the reliability gain from adding re-planning to a bare ReAct loop, since "prevents erroring out" deserves a quantified reliability comparison, not just a qualitative description.

**Step 1 — bare ReAct failure probability.** If a single execution attempt fails with probability $p$, and the loop retries up to $k$ times before hitting `max_retries` and erroring out, the probability the bare loop ultimately fails (never succeeds within $k$ attempts) is $p^k$ — assuming failures are independent across retries, which is optimistic but a reasonable starting approximation.

**Step 2 — re-planning changes what happens on the $k$-th failure.** Instead of erroring out at attempt $k$, a re-planning node generates a *new* plan informed by the accumulated failure context. If the new plan has a different (hopefully lower) failure probability $p' < p$ — because it now accounts for whatever caused the original plan to fail repeatedly — the overall system's failure probability after re-planning is $p^k \cdot (p')^{k'}$ for a further $k'$ attempts under the new plan, which is strictly smaller than $p^k$ alone whenever $p' < 1$, since it's an additional chance to succeed rather than a hard stop.

**Step 3 — bound the benefit honestly.** This isn't unconditional improvement — if the underlying cause of failure is external and unaffected by re-planning (a genuinely broken sensor, not a bad plan), $p'$ may not be meaningfully lower than $p$, and re-planning only delays the eventual failure rather than preventing it. The benefit of re-planning is proportional to how much of the original failure was attributable to a fixable planning deficiency versus an unfixable external condition.

**Step 4 — reflection's effect is on a different axis.** Reflection doesn't change execution failure probability at all — it operates on outputs that already executed successfully without error, catching a different quantity entirely: the probability $q$ that a successfully-executed output nonetheless fails to meet quality criteria. Adding a reflection loop with self-assessment accuracy $a$ reduces the probability of a bad output slipping through undetected to roughly $q(1-a)$ — the residual risk is bounded by how good the model's self-assessment actually is, which is why reflection's real-world value depends heavily on how well-calibrated the reflecting model's own judgment turns out to be.

## Practical pattern

Adding resilience patterns to a ReAct-based agent in the right order and for the right failure mode:

1. start with planning-and-execution as the default structure for anything beyond the simplest single-step task — a dedicated planning call before execution reduces how often you need the recovery patterns below in the first place;
2. add re-planning specifically at the point where a bare ReAct loop would hit `max_retries` and error out — catch that failure explicitly and route it back to the planner with the failure context included, rather than letting the system halt;
3. add reflection specifically after execution completes without error, as a separate quality gate — don't rely on the absence of an execution error as evidence the output is actually good, since these are different questions with different failure signatures;
4. when a reflection loop finds low-quality output, feed the specific deficiency back into the next attempt's context (similar to re-planning's use of failure context) rather than simply retrying blind, so each iteration has genuine new information to work with;
5. monitor how often each pattern actually fires in production — a re-planning node that fires constantly suggests a systemic planning quality issue worth fixing at the source, not just papering over with recovery loops.

## Common traps

- relying on a bare ReAct loop for any task complex enough that its plan might legitimately need mid-execution revision, and discovering the `max_retries` dead end only in production;
- confusing re-planning and reflection as interchangeable recovery mechanisms, when they trigger on different signals (execution failure vs. quality assessment of successful output) and feeding the wrong kind of context into the wrong pattern wastes the recovery attempt;
- adding a reflection loop without any accuracy check on the reflecting model's own self-assessment — if $a$ (self-assessment accuracy) is itself unreliable, the reflection pattern provides much less protection than its presence in the architecture diagram might suggest;
- treating re-planning as a fix for failures that are genuinely external and unfixable by a better plan (a truly broken sensor, an unavailable API) — re-planning only helps when the failure was attributable to plan quality, not environmental conditions outside the agent's control.

## Takeaways

- A bare ReAct loop has a specific, brittle failure mode: it hits `max_retries` and errors out with no recovery path when execution repeatedly fails.
- Planning-and-execution, re-planning, and reflection address three different problems — respectively, giving the agent a coherent plan before acting, recovering from execution failures by generating a new plan informed by what went wrong, and catching quality deficiencies in successfully-executed output that no execution error would ever flag.
- These patterns compose rather than substitute for each other: a mature agentic system typically needs all three, applied at the specific point in the loop where their specific failure signature (bad plan, execution failure, poor-quality-but-error-free output) actually occurs.
