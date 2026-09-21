---
id: a5-02-agent-dressed-as-tool-reusability
title: "Dressing an Agent Up as a Tool"
week: 5
topic: "Act I: Agent or Tool? The Litmus Test"
order: 2
summary: When a reasoning-heavy function is genuinely reusable, the best practice is to expose it through a plain Tool interface — hiding the agent inside so other agents and teams can call it without understanding its internals.
course: ai_agents
---

Once you've internalized that a component can need inference-time reasoning and still be packaged as a Tool, a design question follows immediately: when should you actually do this, and what do you gain? The course's cover-image-generator case study is the cleanest illustration available, precisely because it looks, on the surface, like an obviously simple utility function — and turns out to be an agent in a trench coat the moment you look at what it has to do.

The instinct to expose reasoning-heavy functionality as a Tool interface isn't about hiding complexity for its own sake. It's about giving other consumers — other agents, other teams, other services — a contract they can rely on without needing to understand or maintain the reasoning underneath. That contract is what makes a system composable instead of a tangle of bespoke integrations.

This page works through the case study end to end: why the function needs reasoning, why it's still the right call to expose it as a Tool, and what you gain architecturally from doing so.

## Core intuition

A function can be internally agentic — needing to reason, plan, and adapt — while still presenting a simple, stable, tool-like interface to the outside world. Reusability is the deciding factor: the more a piece of reasoning-heavy functionality is needed by different callers, in different contexts, the stronger the case for wrapping it in a Tool interface rather than leaving it as a bespoke agent only one workflow can invoke.

## Why it matters

Consider a function that generates a contextually relevant cover image for a piece of editorial text, using an image engine like FLUX or a multimodal model. On the surface this looks like a single-purpose utility: text in, image out. But to do it well, the function has to call another tool to extract statistically relevant keywords, read the editorial text and reason over it to understand the actual context (not just the keywords), generate a prompt tailored to the image engine's expectations, and be sensitive to the target audience — including baking in negative guardrails ("don't include X imagery") so the output doesn't embarrass the publication. Every one of those steps is a judgment call that depends on the specific article being processed. This function is, internally, an agent.

If every team that needed a cover image had to reimplement that reasoning pipeline, or worse, understand its internals to call it correctly, the system would fragment. Exposing it as a Tool — a clean, documented interface: "give me editorial text, get back an image" — means any other agent or workflow, including ones written by other teams, can use this capability without knowing or caring that there's an entire keyword-extraction-plus-prompt-generation agent running underneath.

## Instructor framing

Use this case study as the bridge from the abstract decision tree in the previous page to a design habit students will apply for the rest of the course: whenever you notice you've built something reusable that also happens to reason, stop and ask whether the calling code actually needs to know that it reasons. Almost always, the answer is no — and dressing it as a Tool is what lets the caller stop worrying about it. This is also the first place students should notice that "Agent vs. Tool" is not a property of the code, but a property of the *interface contract* you choose to expose.

## Worked example

Walk through the two degrees of freedom the course identifies for ordering the internal steps of the cover-image tool. The **linear flow** approach hard-codes the sequence: extract keywords, then read the article for context, then build the prompt, then call the image engine. This is easy to implement and reason about, and it's the right starting point — sequence and dependencies are usually well understood even when individual steps require judgment.

The **dynamic planner** approach instead hands the sequencing itself to a reasoning model: "here are your available steps, plan out how to use them for this specific article." This is more flexible — the tool could decide, for instance, that a particularly abstract op-ed needs a different research step before prompt generation than a straightforward product review does — but it introduces planning overhead and non-determinism that isn't justified for a task this well-understood at the start of a project. The lesson generalizes: don't reach for a dynamic planner just because you can; reach for one when the linear flow keeps breaking on cases you can't anticipate.

Either way, from the outside, the calling code sees the same interface: `generate_cover_image(editorial_text) -> image`. The internal complexity — linear or planned — is invisible to the caller, and can be swapped from one to the other without touching any code that calls the tool.

## Math explained step by step

Quantify the reusability payoff that justifies the Tool wrapper, since "reusable" is doing real engineering work here, not just sounding nice.

**Step 1 — count the integration cost without a shared interface.** If $n$ teams each need cover-image generation and there is no shared Tool contract, each team either reimplements the reasoning pipeline (cost $c$ per team, total $nc$) or hand-integrates directly with one team's bespoke implementation, incurring a coordination cost that grows roughly with the number of pairwise integrations, $O(n^2)$ in the worst case, as each new caller needs custom glue to talk to an interface that was never designed to be shared.

**Step 2 — count the cost with a shared Tool interface.** Building the Tool interface once costs $c + \epsilon$ (a small integration-hardening premium over building it for a single use), and each of the $n$ callers then pays a fixed, small integration cost $\delta \ll c$ to call it — a documented function signature, not a bespoke handshake. Total cost is $c + \epsilon + n\delta$.

**Step 3 — compare.** The shared-interface cost grows linearly in $n$ with a small slope $\delta$; the no-shared-interface cost grows at least linearly with slope $c$ and can grow quadratically under pairwise integration. For any $n > 1$ where $\delta < c$ (almost always true, since $\delta$ is "call a documented function" and $c$ is "understand and reimplement a reasoning pipeline"), the shared Tool interface wins, and the gap widens with every additional caller.

**Step 4 — the practical threshold.** Even at $n = 2$, the Tool wrapper usually pays for itself, because $\epsilon$ (hardening a working prototype into a documented interface) is typically much smaller than $c$ (building the reasoning pipeline from scratch a second time, badly, under time pressure).

## Practical pattern

When deciding whether to wrap a reasoning-heavy function as a Tool:

1. identify every current and plausible future caller of this functionality — if the honest answer is "just this one workflow, forever," build it as a dedicated Agent and skip the wrapper;
2. if there's a real second caller on the horizon, harden the interface now rather than later — define the input/output contract, write the documentation the MCP tool format expects, and add guardrails (like the negative-prompt sensitivity in the cover-image case) as part of the interface, not as an afterthought bolted on per caller;
3. start with the linear-flow internal implementation unless you already have concrete evidence that step ordering needs to vary per input — add a dynamic planner only once the linear flow demonstrably can't handle the variation you're seeing;
4. keep the reasoning internals swappable behind the stable interface — the whole point of the wrapper is that callers never need to know or care whether version 2 uses a smarter internal agent than version 1.

## Common traps

- building the bespoke, single-caller version first and never revisiting the decision once a second caller appears, leading to duplicated reasoning logic scattered across the codebase;
- over-engineering the first version with a dynamic planner "for future flexibility" before any evidence shows the linear flow is insufficient, adding latency and unpredictability nobody asked for yet;
- exposing the Tool interface without the guardrails baked in (e.g., forgetting the "don't generate unwanted imagery" sensitivity), which pushes safety logic out to every caller instead of centralizing it where the reasoning already lives;
- assuming that because the interface looks like a Tool, the underlying cost profile is tool-like too — a Tool wrapper around an agent still pays LLM latency and cost on every call, and capacity planning needs to reflect that, not the near-free cost of a real deterministic tool.

## Takeaways

- A reasoning-heavy function should be evaluated for reusability separately from whether it needs reasoning at all — the two questions have independent answers, and the combination "needs reasoning AND is reusable" is exactly what should be built as an agent dressed up as a Tool.
- The cover-image generator is internally an agent (it plans, reads context, and reasons about audience sensitivity) but externally a Tool (a stable, documented, swappable interface), and this is the intended pattern, not an inconsistency.
- Start with a linear internal flow and only add dynamic planning once you have concrete evidence the fixed sequence can't handle real-world variation — flexibility you don't need yet is pure overhead.
