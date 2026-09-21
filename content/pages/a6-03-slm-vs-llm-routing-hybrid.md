---
id: a6-03-slm-vs-llm-routing-hybrid
title: "The Insane Extravaganza: Right-Sizing the Model"
week: 6
topic: "Act I: Frameworks and the Physics of Scale"
order: 3
summary: Most calls to frontier LLMs are for trivial tasks a tiny model could handle a thousand times faster — the fix is a hybrid architecture where a rules engine routes atomic tasks to the smallest model that can do the job.
course: ai_agents
---

Here's a number worth sitting with: 80-90% of calls to frontier models like GPT are, empirically, for trivial tasks. Keyword extraction. Formatting. Simple classification. Tasks a model with a hundred million parameters can do locally in a millisecond and a half. And yet the default instinct in a lot of agentic system design is to route everything through the biggest, smartest model available, because it's simple to build and it's never *wrong* to use more intelligence than you need — it's just wasteful, sometimes by four orders of magnitude.

The course calls this the "insane extravaganza" of model usage, and the phrase is doing real work: it's naming a pattern that looks reasonable in isolation (just use the best model, why complicate things) and is actually a systemic waste of latency and cost once you look at the aggregate numbers. The fix isn't complicated once you see it, but it does require giving up the simplicity of "one model handles everything."

## Core intuition

LLM latency is driven by two structural factors: the number of parameters (more parameters means more matrix multiplications per forward pass) and the number of tokens generated (each new token requires an entirely new forward pass, since generation is sequential). Both factors argue for using the smallest model that can reliably accomplish a given task — not the largest model available, and not even a "reasonably capable" middle-sized model chosen out of caution, but the actual floor of what the task requires.

A 100-million-parameter SLM performing a simple task like keyword extraction runs in roughly 1-1.5 milliseconds locally. An API call to a frontier model for the same task takes 2-10 seconds — 10,000 milliseconds, roughly four orders of magnitude slower. For a task that doesn't need frontier-model reasoning, this gap is not a nuance; it's pure waste, repeated on every single call.

## Why it matters

The debate over "SLMs vs. LLMs" framed as a philosophical question is, as the course puts it, silly — the actual decision is engineering common sense once you look at the specific task in front of you, not a general-purpose ideological stance to hold about model size. What matters is that the optimal architecture for most real agentic systems is hybrid: a "big brain" LLM handles the genuinely hard part — complex planning, task decomposition, reasoning about ambiguous, novel situations — while the atomic, well-defined sub-tasks that plan decomposes into get delegated to small, fast, cheap models running as MCP tools.

This matters practically because latency compounds across an agent's loop. An agent that calls a frontier model for every single sub-step of a multi-step task pays the 2-10 second tax repeatedly, even for steps that are, individually, trivial classification or extraction tasks. An agent using the hybrid pattern pays the frontier-model tax only at the planning step, where it's actually earning its cost, and delegates everything downstream to models that respond in single-digit milliseconds.

## Instructor framing

Lead with the 1.5ms-vs-10,000ms comparison before anything else — it's the single number in this material most likely to actually change how a student architects their next agent, because it makes the waste viscerally quantifiable rather than a vague sense that "bigger models cost more." Once that number lands, introduce the routing-by-rules-engine pattern as the concrete mechanism that captures the savings without requiring the system to make an expensive judgment call about model selection on every request — the mechanism matters as much as the motivating number.

## Worked example

Consider the "Mill on the Floss" query from the course: "In which house did the author of Mill on the Floss spend her early childhood years? How did the surroundings influence her later works? Itemize the influences with specific evidence." This cannot be answered in a single pass — it requires planning (identify the author, locate the childhood home, correlate the surroundings with the later works), transformation (turning the natural-language question into search queries), and execution (running searches, gathering facts, synthesizing an itemized answer).

The planning step — deciding *what* needs to happen and in what order — is exactly the kind of task that benefits from a frontier model's reasoning capability; there's no shortcut around needing real judgment here. But once the plan exists, "identify the author of Mill on the Floss" is a lookup, not a reasoning task, and "extract the childhood-home location from this retrieved passage" is extraction, not synthesis. Routing these atomic, well-defined steps to small, fast models backed by MCP tools — while reserving the frontier model for the initial plan and the final itemized synthesis — captures the hybrid pattern's savings without sacrificing the quality of the parts that genuinely need a big brain.

## Math explained step by step

Quantify the aggregate latency and cost savings from routing, since the 80-90%-trivial-calls statistic is only actionable once you see what it implies about total system cost.

**Step 1 — baseline cost, everything routed to frontier.** If an agent makes $n$ sub-calls per task, and every call goes to a frontier model at latency $L_{\text{frontier}} \approx 2\text{-}10\text{s}$ and cost $c_{\text{frontier}}$ per call, total latency is $n \cdot L_{\text{frontier}}$ and total cost is $n \cdot c_{\text{frontier}}$.

**Step 2 — apply the 80-90% triviality statistic.** If a fraction $q \approx 0.8\text{-}0.9$ of those $n$ calls are trivial tasks an SLM could handle at $L_{\text{slm}} \approx 1\text{-}1.5\text{ms}$ and cost $c_{\text{slm}} \ll c_{\text{frontier}}$ (often near-zero marginal cost once the SLM is deployed locally), routing correctly changes total latency to

$$n\big[(1-q) L_{\text{frontier}} + q\, L_{\text{slm}}\big] \approx n(1-q) L_{\text{frontier}}$$

since $q \cdot L_{\text{slm}}$ is negligible relative to $(1-q) L_{\text{frontier}}$ given the four-order-of-magnitude gap between the two latencies.

**Step 3 — see the scale of the reduction.** With $q = 0.85$, total latency drops to roughly $15\%$ of the naive baseline — a $\sim 6.7\times$ speedup — purely from routing, with no change to the frontier model's own capability or the quality of the genuinely hard sub-tasks it still handles.

**Step 4 — the cost side compounds the same way.** Since $c_{\text{slm}} \ll c_{\text{frontier}}$ typically by a similar or larger margin than the latency gap (SLM inference can run on commodity hardware locally, avoiding per-call API billing entirely), the cost reduction from correct routing is at least as dramatic as the latency reduction — routing is simultaneously a latency fix and a cost fix, which is unusually clean as engineering trade-offs go.

## Practical pattern

Building the hybrid routing architecture in practice:

1. classify every sub-task your agent's plan decomposes into as either "requires genuine reasoning/judgment over novel input" (frontier-model territory) or "well-defined extraction, classification, or formatting" (SLM territory) — most sub-tasks, once decomposed, fall into the second category;
2. avoid building an expensive, dynamic "complexity analysis" step that itself calls an LLM to decide which model to route to — this defeats the purpose by adding a frontier-model-scale cost to every routing decision; use a simple, fast rules engine instead, keyed on task type, not runtime LLM judgment;
3. reserve the frontier model specifically for the planning and decomposition step, and for final synthesis steps that need to weigh and combine information from multiple sources — not for every intermediate step in between;
4. deploy the SLMs handling routed sub-tasks as MCP tools (connecting back to the Direct/Gateway/Ray architecture from Week 5), so they benefit from the same production-grade scaling and isolation as any other tool in the system;
5. periodically audit your system's actual call distribution — measure what fraction of your real traffic is landing on the frontier model for tasks that, on inspection, didn't need it, and use that measurement to refine the routing rules over time.

## Common traps

- routing every sub-task to the frontier model by default because it's the path of least implementation effort, silently accepting a 10,000ms-vs-1.5ms tax on the majority of calls that didn't need it;
- building a dynamic, LLM-based complexity classifier to decide routing, which pays a frontier-model-scale cost on the very decision meant to avoid frontier-model-scale costs;
- treating the SLM-vs-LLM choice as a one-time architectural decision made in the abstract, rather than a per-task-type classification that should be revisited as the system's actual call patterns become visible through profiling;
- under-investing in the planning step's model quality in an attempt to save cost everywhere — the hybrid pattern's savings come from *not* wasting frontier-model capability on trivial tasks, not from starving the genuinely hard planning step of the reasoning capability it needs.

## Takeaways

- 80-90% of frontier-model calls in real agentic systems are for tasks a small, fast, cheap SLM could handle — using a frontier model for keyword extraction is a four-order-of-magnitude latency waste (10,000ms vs. 1.5ms), repeated on every call.
- The right architecture is hybrid: a "big brain" LLM handles planning and complex reasoning, while a simple, fast rules engine (not another LLM call) routes atomic, well-defined sub-tasks to small models running as MCP tools.
- Correct routing is simultaneously a latency fix and a cost fix — with roughly 85% of calls routed away from the frontier model, total latency and cost both drop by a comparable large factor, with no loss of quality on the tasks that genuinely need frontier-model reasoning.
