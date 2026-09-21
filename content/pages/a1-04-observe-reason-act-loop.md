---
id: a1-04-observe-reason-act-loop
title: "The Observe-Reason-Act Loop"
week: 1
topic: "Act II: What Is An Agent"
order: 4
summary: An AI agent is formally defined by a repeating cycle — observe the environment, reason about a plan, act to change the environment's state — that continues until the goal is recognized as met.
course: ai_agents
---

Strip away every framework name, every buzzword, and every vendor slide, and an AI agent reduces to one formal structure repeated over and over: it observes the state of some environment, it reasons about what action would move that environment closer to a goal, and it acts to actually change that state. Then it observes again, because the world it just acted on is no longer the world it started with. This loop — observe, reason, act, observe — is the entire definition. Everything else this course teaches is either a way of making one stage of the loop smarter, or a way of managing what happens when the loop doesn't converge.

It's worth noticing how unglamorous this definition is. A thermostat arguably observes and acts. A robot vacuum clearly does. What makes an *AI* agent different is not the loop's existence — it's the quality of the reasoning stage: whether the system can genuinely form and revise a plan, versus mechanically mapping fixed inputs to fixed outputs.

## Core intuition

An agent exists inside an environment with a goal that implicitly defines its role. It perceives that environment through some observation mechanism, reasons about what actions its available tools make possible, and then acts through those tools to change the environment's state. This cycle continues, without a human re-issuing instructions at every step, until the agent recognizes the goal has been met — and recognizing that termination condition is itself part of the reasoning the agent must do, to avoid looping forever.

## Why it matters

This loop is what separates an agent from a script. A traditional program executes a fixed sequence regardless of what it observes mid-execution (or observes very little at all). An agent's next action is *conditioned on* what it just observed, which is what allows it to handle situations its designer never explicitly anticipated. That adaptability is the entire value proposition of agentic systems over hardwired workflows — and it is also exactly the source of the reliability problems this course spends thirteen more weeks addressing, because a system that adapts to what it observes can adapt its way into a wrong plan just as easily as a right one.

## Instructor framing

Make students trace this loop explicitly for every example that follows in the course, including ones that don't look like "agents" at first glance. A thermostat's loop (observe temperature, decide, adjust) is deliberately included in the source material specifically to sharpen the boundary: it has the loop's *shape* but arguably not its *reasoning* — the mapping from observed temperature to action is fixed and mechanical, not a genuine plan formed and revised in response to novel circumstances. Come back to this boundary case whenever the course later asks "is this an agent or a workflow?"

## Worked example

Take the robotic vacuum cleaner example directly from this week's material. Its environment is the room's layout, furniture, and dust distribution — and critically, the agent doesn't need to know this environment in advance; it can learn it through exploration. Its goal is "clean the room in the most efficient manner." Its observation mechanism is cameras, dust sensors, and proximity detectors. Its reasoning stage computes an efficient cleaning path *even in an unfamiliar room* — this is the part that's genuinely agentic, because a hardwired vacuum would need someone to have pre-mapped every room it will ever clean. Its action stage is motors and suction mechanisms executing that plan. The loop repeats: observe the now-partially-cleaned room, reason about what's left, act again, until the goal condition — room clean — is recognized as satisfied and the loop halts.

## Math explained step by step

The loop's termination condition is worth formalizing, because "the agent must recognize when the goal has been met to avoid an infinite loop" is a real engineering constraint, not a throwaway line.

**Step 1 — define the environment state and goal predicate.** Let $s_t$ be the environment's state at loop iteration $t$, and let $G(s)$ be a boolean goal predicate that is true exactly when the state satisfies the objective (room clean, review submitted, castle built).

**Step 2 — define one loop iteration as a state transition.** Each iteration applies $s_{t+1} = \text{Act}(\text{Reason}(\text{Observe}(s_t)))$ — observation extracts a (possibly partial or noisy) representation of $s_t$, reasoning selects an action from the available tool set, and acting transforms the state.

**Step 3 — the halting condition is a separate check, not a free byproduct of acting.** The loop runs while $\lnot G(s_t)$ and halts the first iteration where $G(s_t)$ becomes true. If $G$ is poorly specified — too vague, or not actually checkable from what the agent can observe — the loop has no principled way to know it's done, and will either halt prematurely (declaring success too early) or never halt (looping on unnecessary re-cleaning, or in the software case, repeatedly re-querying tools that already answered the question).

**Step 4 — see the direct cost implication.** Every extra iteration before $G$ is satisfied costs one more Observe-Reason-Act cycle, and each cycle typically costs at least one LLM call (the reasoning stage) plus one or more tool calls (the action stage). A poorly specified $G$ doesn't just risk incorrect behavior — it directly inflates latency and API cost, since the agent will iterate longer than necessary probing for a termination signal it cannot cleanly detect.

## Practical pattern

1. Before building any agent, write down $G(s)$ explicitly and ask whether it is actually computable from what the agent can observe — an unobservable goal condition guarantees loop trouble later.
2. Log every (observe, reason, act) triple during development — this is the raw trace that lets you see exactly where a loop diverged from the intended plan, and it's the foundation of the observability practices this course covers in Week 3.
3. Build in an explicit maximum iteration count as a safety net independent of $G$, so a malformed goal predicate produces a bounded failure (a clear "I couldn't complete this") rather than an unbounded, silently expensive loop.
4. Treat the "reason" stage as the one doing the real intellectual work — the observe and act stages are usually mechanical (an API call, a sensor read); most of an agent's reliability problems live in how well it reasons over what it just observed.

## Common traps

- Confusing a fixed observe-decide-act mapping (a thermostat, a simple webhook) for genuine agentic reasoning — the loop's shape is not sufficient; the reasoning stage must actually form and revise a plan.
- Leaving the goal predicate $G(s)$ implicit or vague ("give a good answer") rather than explicit and checkable, which produces unpredictable termination behavior.
- Forgetting that observation is often partial or noisy — an agent's plan is only as good as what it can actually perceive of the true state, not the full state itself.
- Omitting a hard iteration cap, so a subtly malformed goal condition produces an agent that loops indefinitely and burns cost without bound.

## Takeaways

- Every AI agent, regardless of framework or domain, reduces to the same observe-reason-act loop repeating until a goal condition is satisfied.
- The reasoning stage — not the mere existence of the loop — is what distinguishes a genuine agent from a reactive sensor-actuator system like a thermostat.
- The goal predicate $G(s)$ must be both explicit and observable, or the loop's termination behavior becomes unpredictable and costly.
- Logging every loop iteration is the foundation for the observability and reliability engineering the rest of this bootcamp builds on.
