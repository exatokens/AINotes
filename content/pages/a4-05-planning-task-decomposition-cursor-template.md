---
id: a4-05-planning-task-decomposition-cursor-template
title: "Plan First: The Cursor Template for Agent Behavior"
week: 4
topic: "Act II: Architecting Reliable Agents"
order: 5
summary: The first thing a well-behaved agent should do is itemize a task list before acting — the exact pattern visible in coding assistants like Cursor — converting an opaque single-shot generation into a visible, checkable, revisable plan.
course: ai_agents
---

Amid this week's heavier material on stochasticity and architecture sits a small, concrete, almost throwaway observation that turns out to be one of the more immediately actionable design patterns in the whole bootcamp: watch what a good coding agent does the instant you give it a task. It doesn't dive straight into generating a final answer. It itemizes — producing an explicit list of the sub-tasks it believes the goal requires, then works through that list one item at a time, checking items off as it completes them. This week names this directly: "Cursor is a good template for how your agent should behave."

It's worth taking this observation more seriously than its casualness suggests, because it's a direct, practical implementation of the observe-reason-act loop's reasoning stage, made *visible* rather than opaque — and visibility, as this bootcamp keeps discovering in different contexts, is what converts an unmeasurable, untrustable process into a measurable, trustable one.

## Core intuition

An agent that plans explicitly — producing a visible, itemized task list before executing any of it — converts its internal reasoning from an opaque, single-shot process into an inspectable, revisable artifact. This has two distinct benefits that are easy to conflate but worth separating: it improves the agent's own execution (a decomposed plan is easier to execute correctly step by step than a complex goal attempted in one pass), and it improves the *human's* ability to trust, verify, and intervene in the agent's behavior before costly or irreversible actions are taken.

## Why it matters

This pattern directly addresses the enterprise reliability crisis from earlier this week at a specific, practical layer: instead of trying to eliminate stochasticity at the token-generation level (which the earlier pages show is only partially achievable), explicit planning manages stochasticity's *consequences* by exposing the agent's intended sequence of actions before most of them are irreversibly executed. A wrong plan, caught and corrected before execution, costs far less than a wrong action already taken — this is the same "test before act" logic behind the dark-factory digital-twin pattern from Week 1, applied to software agents rather than physical robots.

## Instructor framing

Connect this explicitly backward to the ReAct pattern from Week 3: an itemized task list is what ReAct's interleaved reasoning-then-acting looks like when made maximally visible and maximally granular. It's also the natural place to apply a human-in-the-loop checkpoint — not on every individual token the agent generates (impractical and would defeat the purpose of autonomy) but on the plan itself, before execution begins, which is a much cheaper and more tractable point of human oversight.

## Worked example

Return to the shipping help-desk agent mini-project referenced this week. Given the goal "resolve this customer's shipping delay complaint," a non-planning agent might generate a single, monolithic response attempting to diagnose the issue, check order status, and draft a reply all in one un-decomposed pass — and if any one part of that fused reasoning goes wrong (misreading the order status, say), the error propagates silently into the final drafted reply with no visible seam where a reviewer could have caught it. A planning agent instead first produces an explicit list: (1) look up the order and shipping status, (2) determine whether the delay is carrier-side or fulfillment-side, (3) check whether this customer has a history of similar complaints (informing tone and whether escalation is warranted), (4) draft a response appropriate to the diagnosis, (5) flag for human review if the delay exceeds a compensation threshold. Each item can now be executed, and audited, independently — if step 2's diagnosis turns out wrong, that specific step is where the audit trail shows the error, not an undifferentiated final output that's simply "wrong" for reasons requiring the entire reasoning process to be re-derived from scratch to diagnose.

## Math explained step by step

The reliability benefit of explicit decomposition can be quantified using the same per-step-error compounding logic from earlier weeks, applied specifically to the trade-off between monolithic and decomposed execution.

**Step 1 — model monolithic execution's error rate.** Suppose a complex task, attempted as a single undivided reasoning step, succeeds with probability $p_{\text{mono}}$ — a single number capturing the joint difficulty of every sub-problem bundled together, with no visibility into which part, if any, went wrong when it fails.

**Step 2 — model decomposed execution's error rate.** Suppose the same task, decomposed into $k$ explicit sub-steps each with independent-ish success probability $p_i$, has overall success probability $\prod_{i=1}^k p_i$ if no correction is possible — this can actually be *worse* than $p_{\text{mono}}$ if $k$ is large and errors compound multiplicatively with no intervention, which is an important caveat: decomposition alone, with no checkpointing, does not automatically improve reliability.

**Step 3 — see what visibility and checkpointing add.** If each sub-step's output is checked (by a human, or by an automated validator) before the next step proceeds, and a failed sub-step can be corrected with probability $r$ before continuing, the effective probability of completing all $k$ steps successfully becomes $\prod_{i=1}^k \big(p_i + (1-p_i) r\big)$ — strictly higher than the uncorrected $\prod_i p_i$ whenever $r > 0$, and this gain compounds across every one of the $k$ steps, unlike the monolithic case where there is only one step at which correction could even be attempted, applied to the entire bundled task at once.

**Step 4 — see why the visible plan is what makes $r > 0$ achievable at all.** Correction probability $r$ depends entirely on whether an error is *detectable* at the point it occurs. In the monolithic case, an error in an early implicit sub-reasoning step is invisible until the final output is produced, by which point diagnosing which part went wrong requires re-deriving the whole reasoning chain — effectively driving $r$ toward zero in practice, even if a human reviewer is technically available. The explicit, itemized plan is precisely what makes each $p_i$'s outcome separately visible and separately correctable, which is the entire mechanism behind the reliability gain in Step 3.

## Practical pattern

1. Design agents to produce an explicit, itemized task list as their first action on any non-trivial goal, before executing any of the plan's steps — treat this as a required first output, not an optional nicety.
2. Insert checkpoints after high-stakes or hard-to-reverse steps specifically, where a corrected error ($r > 0$) is most valuable — not uniformly after every step, which would erode the efficiency gains of autonomy.
3. Log each plan step's outcome individually, not just the final aggregated result — this is what makes post-hoc debugging tractable, turning "the agent gave a wrong answer" into "step 3 of the plan misdiagnosed the order status."
4. For human-in-the-loop review, present the plan itself (not just raw token-level output) as the primary review artifact — reviewing a five-item plan is far cheaper and more tractable for a human than reviewing an entire undifferentiated final response for correctness.

## Common traps

- Decomposing a task into explicit steps without adding any checkpointing or correction mechanism between them — per the math above, this can leave reliability unchanged or even worsen it if per-step error compounds unmitigated across a longer step sequence.
- Treating explicit planning as purely a UX nicety (making the agent "feel" more transparent) rather than recognizing it as a direct reliability mechanism that makes correction probability $r$ achievable in the first place.
- Inserting human checkpoints after every single step regardless of stakes, eroding the efficiency and autonomy benefits that motivated using an agent in the first place.
- Logging only the agent's final output rather than each intermediate plan step's outcome, making post-hoc failure diagnosis require re-deriving the entire reasoning chain from scratch.

## Takeaways

- Well-behaved agents plan explicitly before acting — producing an itemized, visible task list is a direct, practical implementation of the observe-reason-act loop's reasoning stage made inspectable rather than opaque.
- Decomposition alone does not automatically improve reliability; it must be paired with checkpointing and correction to actually raise the probability of overall task success.
- Visibility into individual plan steps is what makes error correction probability ($r$) achievable at all — an undifferentiated monolithic output makes post-hoc correction nearly impossible even when a human reviewer is available.
- Human-in-the-loop review is far more tractable and cost-effective when applied to an agent's explicit plan than when applied to raw, undifferentiated final output.
