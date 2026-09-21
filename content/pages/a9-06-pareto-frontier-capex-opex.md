---
id: a9-06-pareto-frontier-capex-opex
title: "The Pareto Frontier: CapEx, OpEx, and the RAG-Versus-Fine-Tuning Trade"
week: 9
topic: "Act I: The Escalation Ladder for Agent Intelligence"
order: 6
summary: RAG and fine-tuning sit at different points on a CapEx-versus-OpEx Pareto frontier, and the right choice is not "which is better" but "which point on the frontier matches your traffic volume."
course: ai_agents
---

A senator hosts an Indian MP and, wanting to seem impressively resourceful, points at a bridge over a river: "Ten percent," he winks, meaning it cost him only a tenth of the sanctioned budget and he pocketed the rest, and yet a functional bridge still exists. The MP, hosting the senator in an even grander palace, points to the same kind of river and asks, "Do you see the bridge?" "No bridge," the senator admits. "One hundred percent," the MP replies — he kept the entire budget, and there is no bridge at all. Both are, in a narrow technical sense, Pareto-optimal: each maximized one objective (personal profit) at the total expense of another (a functioning bridge). Engineering is never about finding "the" right solution — it's about knowingly choosing a point on a frontier of unavoidable trade-offs.

This page applies that frontier explicitly to the RAG-versus-fine-tuning decision, using the two variables that actually decide it in production: capital expense (CapEx, the cost to set a system up) and operational expense (OpEx, the recurring cost to run it).

## Core intuition

Engineering is multi-objective optimization under constraints. A **Pareto-efficient frontier** is the set of solutions where you cannot improve one objective without worsening another; any point on that curve is **Pareto-optimal**, while a point strictly inside the frontier is **suboptimal** — an inefficient use of resources regardless of preference.

Applied to RAG versus fine-tuning: **RAG** has very low CapEx (easy to stand up — embed, index, retrieve) but very high OpEx (large context windows and recurring token costs, paid on every single query). **Supervised Fine-Tuning (SFT)** has medium CapEx and low OpEx. **Reinforcement Learning (RLFT)** has very high CapEx and low OpEx. Roughly: $\text{RLFT}_{\text{CapEx}} \gg \text{SFT}_{\text{CapEx}} \gg \text{RAG}_{\text{CapEx}}$, while $\text{RAG}_{\text{OpEx}} \gg (\text{SFT}_{\text{OpEx}}, \text{RLFT}_{\text{OpEx}})$.

## Why it matters

This single trade-off resolves an argument that otherwise sounds like taste: "RAG is dead" versus "fine-tuning is a distraction." Neither claim is really about technical superiority — it's about traffic volume. A low-traffic service pays RAG's high per-query OpEx rarely enough that total cost stays low, so it's rational to save on upfront CapEx and just use RAG. A high-traffic service pays that same per-query OpEx *millions of times*, so it dominates total cost, and it becomes rational to absorb fine-tuning's higher CapEx once in exchange for a low OpEx that repeats forever. The "right" answer flips entirely based on a variable — expected query volume — that has nothing to do with which technique is conceptually more elegant.

## Instructor framing

Anchor this to the previous page's knowledge-versus-reasoning dichotomy: that page decides *whether* RAG or fine-tuning is even the correct category of remedy; this page decides, once you're in the RAG-eligible knowledge-gap territory, *whether it's still economically the right choice at your traffic volume*. A team can correctly diagnose a knowledge gap, correctly reach for RAG, and still be making a Pareto-suboptimal economic decision if their service is high-traffic enough that the OpEx bill dwarfs the CapEx they saved.

## Worked example

A farmer uses a tractor every day (high volume) but a laptop rarely (low volume); his Pareto-optimal allocation is high CapEx on an efficient tractor and low CapEx on a cheap laptop. An AI engineer uses a laptop every day but a tractor rarely (mowing the lawn); the allocation flips — high CapEx on a powerful laptop, low CapEx on a basic tractor. Neither farmer nor engineer is wrong; they are optimizing the same frontier against opposite usage patterns.

Cursor's own history illustrates the same logic inside one company. Their original $20-a-month plan is a Pareto trade: a subscription fee balanced against the OpEx of calling a powerful external frontier model per token, with users downgraded to a weaker model once they exhaust their allotment — a RAG-and-API-heavy, low-CapEx, high-OpEx point on the frontier, appropriate while usage volume and product-market fit were still uncertain. Their subsequent move to fine-tune (and reportedly train) their own model is a deliberate shift to a different point on the frontier: absorb high internal CapEx now, in exchange for lower long-run internal OpEx per query — a bet that their traffic volume has grown large enough to make that trade pay off. Similarly, the Indian Civil Service's choice between promotees (decades of experience, less raw brilliance) and IAS officers straight from exam (brilliant, zero experience) for District Magistrate posts is two Pareto-optimal solutions on a Brilliance-versus-Experience frontier — a "brilliant officer with twenty years' experience" would be ideal but is not an available point on the curve.

## Math explained step by step

Derive the volume-based break-even point explicitly.

**Step 1 — total cost as a function of volume.** For a service handling $n$ queries, total cost under approach $i$ is $\text{Cost}_i(n) = C_i + n \cdot o_i$, where $C_i$ is one-time CapEx and $o_i$ is per-query OpEx.

**Step 2 — plug in the ordering.** For RAG: $C_{\text{RAG}}$ small, $o_{\text{RAG}}$ large. For SFT: $C_{\text{SFT}}$ medium, $o_{\text{SFT}}$ small. So $\text{Cost}_{\text{RAG}}(n) = C_{\text{RAG}} + n \cdot o_{\text{RAG}}$ and $\text{Cost}_{\text{SFT}}(n) = C_{\text{SFT}} + n \cdot o_{\text{SFT}}$.

**Step 3 — solve for the break-even volume $n^*$.** Setting the two costs equal: $C_{\text{RAG}} + n^* o_{\text{RAG}} = C_{\text{SFT}} + n^* o_{\text{SFT}}$, so $n^* = \dfrac{C_{\text{SFT}} - C_{\text{RAG}}}{o_{\text{RAG}} - o_{\text{SFT}}}$. Below $n^*$, RAG's lower CapEx keeps it cheaper overall; above $n^*$, SFT's lower OpEx wins out because it's multiplied by a larger $n$.

**Step 4 — read the frontier as a decision rule, not a fixed answer.** $n^*$ is specific to your actual $C_i$ and $o_i$ figures — model prices, context sizes, and hosting costs all move it — so "low traffic → RAG, high traffic → fine-tune" is a *shape* of the correct answer, not a universal threshold. Any team applying this must estimate its own $n^*$ from its own costs before committing.

## Practical pattern

1. before choosing RAG or fine-tuning, estimate your expected query volume $n$ over the system's planned lifetime, not just at launch — a service expected to scale needs $n^*$ computed against its *future* traffic, not today's;
2. measure your actual $C_i$ and $o_i$ for each candidate approach (retrieval infra cost and per-query token cost for RAG; training run cost and per-query inference cost for fine-tuning) rather than reasoning from the general shape of the trade-off alone;
3. treat this as a re-evaluated decision, not a one-time one — Cursor's shift from RAG-and-API to internal fine-tuning is evidence that the right point on the frontier moves as a product's volume grows, and today's correct choice may not be tomorrow's;
4. resist "RAG is dead" or "fine-tuning is dead" takes as universal claims — they are, at best, claims about where a specific product's $n$ sits relative to its specific $n^*$.

## Common traps

- choosing a technique based on which is "better" in the abstract, rather than computing where your actual traffic volume sits relative to the CapEx/OpEx break-even point;
- locking in a low-traffic-appropriate RAG architecture and failing to revisit the decision as volume grows past $n^*$, silently letting OpEx dominate total cost;
- treating CapEx as a one-time sunk decision immune to re-evaluation — Pareto-optimal points are optimal *given current constraints*, and constraints (traffic, model prices) change;
- ignoring that RLFT's CapEx is typically far higher than SFT's, meaning the top of the escalation ladder should only be reached for when its low OpEx is being amortized over enormous volume or when SFT's ceiling has already been proven insufficient.

## Takeaways

- RAG and fine-tuning are not competing on quality alone — they occupy different points on a CapEx-versus-OpEx Pareto frontier, and the right choice depends on expected traffic volume.
- Low-traffic services rationally favor RAG's low CapEx; high-traffic services rationally favor fine-tuning's low OpEx, because OpEx is paid per query and compounds with volume.
- The break-even query volume $n^*$ is computable from your own cost figures — use it, rather than general intuition, to decide.
- Points on the frontier are not permanent: a product's growth in volume can rationally justify migrating from a RAG-heavy architecture to an internally fine-tuned one, as illustrated by real production shifts in the industry.
