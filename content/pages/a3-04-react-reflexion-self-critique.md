---
id: a3-04-react-reflexion-self-critique
title: "ReAct and Reflexion: Closing the Loop Between Thinking and Refining"
week: 3
topic: "Act II: The Prompting Toolkit"
order: 4
summary: ReAct bridges pure prompting to genuine agentic behavior by interleaving reasoning and acting; Reflexion adds a self-refinement loop on top, and the pair-agent pattern (editor / senior editor) operationalizes it with an explicit checklist rather than a vague "do better."
course: ai_agents
---

Two techniques in this week's prompting catalogue deserve to be pulled out and treated separately from the rest, because they aren't really prompting tricks in the narrow sense — they're the specific bridge between "an LLM that answers questions" and "an agent that observes, decides, and acts," and between "an agent that answers once" and "an agent that catches its own mistakes before you see them." ReAct is the first bridge. Reflexion, and the pair-agent pattern built on top of it, is the second.

## Core intuition

ReAct (Reason and Act) is the technique — and the paper — credited with showing that an LLM can genuinely function as an agent: rather than answering in one shot, the model interleaves explicit reasoning steps with explicit actions, observing the results of each action before deciding the next one. This is, almost literally, the observe-reason-act loop from Week 1 implemented as a prompting pattern rather than as a full external architecture. Reflexion takes a completed attempt and asks the model to reflect on it, evaluate it, and refine it — self-critique as an explicit, repeatable step rather than a one-off request.

## Why it matters

ReAct matters historically because it's the conceptual missing link between "LLMs are good at language" and "LLMs can be the reasoning core of an autonomous agent" — before this framing, using an LLM as an agent's brain wasn't an obvious design choice at all. Reflexion matters practically because it operationalizes the critique-and-reflect pattern from Week 1 into something concrete enough to build a reliable pipeline around: a checklist-driven, paired-agent architecture rather than a vague hope that "asking it to double-check" will work.

## Instructor framing

Draw the direct line from ReAct's reasoning-then-acting interleaving to this week's earlier axiom-of-measurement material: ReAct produces an observable *trace* — a sequence of reasoning steps and actions — which is exactly the kind of artifact that traceability and observability platforms (LangFuse, Arize) are built to capture and audit. A system built without ReAct's explicit interleaving often produces only a final answer with no visible reasoning trace, which makes debugging a failure close to impossible; a system built with it hands you a step-by-step record of exactly where things went wrong.

## Worked example

Consider a research agent tasked with answering "what was the main cause of the 2010 flash crash?" Under a ReAct pattern, the model doesn't answer directly from parametric memory. It reasons ("I should verify this with a search rather than relying on memory, since financial event details are easy to misremember"), acts (calls a search tool), observes the results, reasons again ("this source mentions a large sell order interacting with high-frequency trading algorithms — I should check a second source to confirm this isn't a single outlier account"), acts again (a second search), and only then produces a final answer grounded in the observed evidence trail. Now layer Reflexion on top using the pair-agent pattern: a "researcher" agent produces this answer, and a separate "senior researcher" agent reviews it against an explicit checklist — does the answer cite at least two independent sources? does it distinguish confirmed causes from speculative ones? is the claimed mechanism actually stated in the retrieved evidence, or inferred beyond what the sources support? If the checklist isn't satisfied, the senior researcher sends the task back to the researcher agent with specific, itemized feedback, and the cycle repeats until the checklist passes or a maximum iteration count is reached — orchestration frameworks like LangGraph implement this as conditional forwarding, hardwiring the "send back if checklist fails" logic rather than leaving it to chance.

## Math explained step by step

The pair-agent Reflexion pattern is worth quantifying the same way the Week 1 critique-and-reflection page did, but extended to *repeated* iteration with an explicit checklist, since that's the operational difference this week adds.

**Step 1 — define per-iteration checklist pass probability.** Let $p$ be the probability that, on any given iteration, the researcher agent's revised output satisfies the full checklist as judged by the senior researcher agent. Assume, for a first approximation, that each iteration is an independent attempt with the same $p$ (a simplification — in practice $p$ should rise with iteration count as feedback accumulates, but the independent case gives a useful lower bound).

**Step 2 — compute the probability of eventual success within $k$ iterations.** The probability that at least one of $k$ independent attempts passes the checklist is $1 - (1-p)^k$ — this grows quickly even for modest $p$: at $p = 0.5$, three iterations already give a $1 - 0.5^3 = 87.5\%$ chance of eventual success, versus $50\%$ for a single unrefined attempt.

**Step 3 — account for the more realistic case where feedback actually improves $p$ across iterations.** If each iteration's specific, itemized feedback (rather than a vague "do better") measurably increases the probability of passing on the next attempt — call it $p_1 < p_2 < p_3 \ldots$ — then the true success probability after $k$ iterations, $1 - \prod_{i=1}^k (1-p_i)$, converges even faster than the independent-$p$ case in Step 2. This is the specific advantage of an *explicit checklist* over a vague self-critique prompt: a checklist gives concrete, itemized feedback ("missing a second source," "claim not supported by evidence") that plausibly raises $p_i$ each round, whereas a vague "can you do better" gives the model less specific signal about what to fix, keeping $p_i$ flatter across iterations.

**Step 4 — connect this to the maximum-iteration cap from the observe-reason-act loop page.** Since $1 - (1-p)^k \to 1$ as $k \to \infty$ regardless of how small $p$ is, an unbounded Reflexion loop will eventually "succeed" even against a very weak checklist-pass probability per round — which is exactly why a hard iteration cap (from Week 1's loop-termination discussion) remains necessary: without one, a persistently low $p$ produces an expensive, slow convergence rather than a fast failure that tells you the checklist or the underlying task specification needs rethinking.

## Practical pattern

1. Implement multi-step agentic tasks using an explicit ReAct-style interleaving of reasoning and action, and log every reason/act/observe triple — this trace is both your debugging tool and your evidence of groundedness.
2. Build self-refinement as a paired-agent architecture (a generator and a separate, explicitly instructed reviewer) rather than a single agent asked to critique itself in the same context, when the stakes justify the added cost — a genuinely separate reviewer role tends to apply more scrutiny, mirroring how a human reviewer catches more than a self-reviewing author.
3. Make the reviewer's checklist explicit and itemized, not a vague "is this good?" — itemized feedback plausibly raises the per-iteration success probability faster than generic critique, per the math above.
4. Cap the number of Reflexion iterations explicitly, and treat hitting the cap as a signal to inspect the checklist or task specification itself, not just as a system failure to route around silently.

## Common traps

- Treating a single-shot LLM call, with no interleaved reasoning-action-observation cycle, as equivalent to a ReAct-style agent — the interleaving and the resulting trace are the actual point, not just the vocabulary.
- Building a self-critique loop with vague feedback ("can you improve this?") when an explicit, itemized checklist would plausibly raise the per-iteration success probability faster and make failures more diagnosable.
- Running a Reflexion loop with no maximum iteration cap, on the assumption that "it'll eventually pass" is an acceptable substitute for actually fixing a low per-iteration pass probability.
- Using a single agent to critique its own output in the same context window rather than a genuinely separate reviewer role, missing the scrutiny asymmetry that a distinct evaluative role tends to bring.

## Takeaways

- ReAct is the technique that operationalizes the observe-reason-act loop as an explicit, interleaved prompting pattern — it's the historical bridge from "LLM as text generator" to "LLM as agent's reasoning core."
- Reflexion adds a self-refinement loop, and the pair-agent (editor / senior editor) pattern operationalizes it with an explicit, itemized checklist rather than vague self-critique.
- Repeated Reflexion iterations compound success probability quickly, especially when specific feedback measurably raises the per-iteration pass rate — but this same compounding is exactly why an explicit iteration cap remains necessary.
- Explicit, itemized checklists outperform vague "do better" prompts because they give the generator concrete signal about what specifically to fix on the next attempt.
