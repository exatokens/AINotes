---
id: a1-06-agent-tool-duality
title: "Agent or Tool? The Reusability Test"
week: 1
topic: "Act II: What Is An Agent"
order: 6
summary: Whether a function using an LLM is an "agent" or merely a "tool" hinges on reusability, not on whether it invokes a language model — and the distinction is contextual, since agents can themselves serve as tools to other agents.
course: ai_agents
---

Once you accept that agents are defined by autonomous decision-making rather than by simply calling an LLM, an uncomfortable question follows immediately: a function that summarizes text uses a language model to do genuinely sophisticated work — so is it an agent? The honest answer, worked out through this week's HR self-review project, is *usually no* — and the reasoning behind that "no" turns out to be one of the more practically useful architectural distinctions in the whole bootcamp.

The common misconception is that "uses an LLM" is the dividing line. It isn't. A simple function that capitalizes a string is obviously a tool — nobody would argue otherwise. What's less obvious is that a *complex* tool that summarizes an entire document, even though it requires real language understanding, remains a tool from an architectural standpoint. The dividing line is reusability, not sophistication.

## Core intuition

A function should be classified as a tool if its usefulness is *horizontal* — it transcends the specific application you're building and would be equally useful to a completely different team solving a completely different problem. A function should be classified as an agent if its logic is specific to this application's unique goals and reasoning, even if it happens to be implemented with an LLM under the hood.

## Why it matters

Getting this distinction right early has a direct payoff in system architecture. Tools are natural candidates to become shared, centrally hosted services — accessible to many different agentic systems across an organization via a protocol like MCP. Agents, by contrast, are the application-specific reasoning components that decide *which* tools to call and *when*. Misclassifying an agent as a tool (or vice versa) leads to either over-centralizing genuinely bespoke logic, or under-sharing genuinely reusable capability and rebuilding it redundantly across every team that needs it.

## Instructor framing

Push students past the surface-level question "does this use an LLM?" to the actual test: *would the legal department, or the finance department, plausibly want this exact function for a completely different purpose?* If yes, it's a tool, and it belongs on a shared server, not buried inside one application's codebase. If the function's entire reason for existing is tied to this one application's specific goal, it's an agent — even if, architecturally, you build it today as a thin wrapper that could later be promoted to a tool if another team asks for it.

## Worked example

Walk through the actual HR self-review tool's feature list, exactly as the recap decides it. **Summarization** — turning a long review into a tight digest — is a horizontal capability that a legal department drafting contract summaries would want just as much as HR does; it's a tool, ideally hosted centrally and exposed via MCP. **Rationalized text** — fixing grammar and typos without changing meaning — is equally horizontal; any application handling user-submitted prose could use it; it's a tool. **Extracting and ranking key achievements from a performance review**, by contrast, is specific to this exact use case — a finance department building a revenue-projection tool has no analogous need for "extract achievements from a review" logic; it's an agent. The best practice noted in the source material is instructive: even though "extract key achievements" is built as an agent today, its core logic should be written independently of any specific orchestration framework, with the agent acting as a thin shim around that core code — because you should always suspect that today's bespoke agent might become tomorrow's requested tool, and you don't want framework lock-in blocking that promotion. Finally, the **metrics radar-graph generator** is judged to be inherently tied to this application's specific rubric (clarity, completeness, outcome-focus) and stays an agent.

## Math explained step by step

The reusability test has a clean way to quantify "horizontal" versus "specific," using the number of distinct applications that would plausibly invoke the function.

**Step 1 — define horizontal value as breadth of applicability.** For a candidate function $f$, let $D(f)$ be the number of distinct application domains in an organization that would want to call $f$ unmodified or with only trivial parameterization (summarization: legal, HR, finance, support — many; achievement-ranking-from-a-review: essentially one).

**Step 2 — set a threshold rule.** Classify $f$ as a tool if $D(f) \geq 2$ (at least one domain beyond the one that motivated building it), and as an agent-specific component if $D(f) = 1$.

**Step 3 — account for the cost of getting the classification wrong in each direction.** Misclassifying a tool as an agent-specific component means it gets rebuilt independently $D(f) - 1$ times across the organization — a direct, multiplying engineering cost. Misclassifying an agent-specific component as a general tool means over-generalizing an interface for a use case that doesn't actually exist yet, adding unnecessary abstraction cost for zero realized benefit.

**Step 4 — use the "thin shim" pattern to hedge under uncertainty.** When $D(f)$ is genuinely uncertain at build time (you don't yet know if another team wants it), building the core logic independent of the orchestration framework and wrapping it in a thin agent shim keeps the promotion cost from agent to tool low — you're not paying the full generalization cost up front, but you're not locking yourself out of it either.

## Practical pattern

1. For every new function in an agentic system, ask explicitly: would at least one other domain in the organization plausibly want this exact capability? If yes, build and host it as a tool from the start.
2. If a function is application-specific today but plausibly generalizable tomorrow, write its core logic independently of your orchestration framework (LangGraph, CrewAI, etc.), and wrap it in a thin agent shim — this keeps a future promotion to "shared tool" cheap.
3. Remember that the agent/tool distinction is relative to perspective, not absolute: a specialized agent (e.g., a "marble-sourcing agent") can itself be exposed as a tool to a higher-level orchestrating agent, exactly as an individual employee is an autonomous agent from their own perspective but a "tool" from their manager's perspective pursuing a larger organizational goal.
4. Resist the urge to centralize everything as a "tool" for the sake of tidiness — over-generalizing an interface for a capability only one application will ever use adds abstraction cost without a corresponding reuse benefit.

## Common traps

- Assuming "uses an LLM" automatically means "is an agent" — sophistication of implementation is not the test; reusability across domains is.
- Failing to write reusable logic independently of the orchestration framework, so that promoting an agent-specific component into a shared tool later requires a costly rewrite rather than a thin re-wrapping.
- Treating the agent/tool label as a permanent, absolute property of a piece of code rather than a contextual, perspective-dependent classification that can change as the organization's needs evolve.
- Over-centralizing genuinely bespoke, single-purpose logic as a "shared tool" before any second consumer has actually asked for it, adding unnecessary interface complexity.

## Takeaways

- The dividing line between an agent and a tool is reusability across application domains, not whether an LLM is involved.
- A complex, LLM-powered function (summarization, grammar correction) is still architecturally a tool if its value is horizontal across many use cases.
- Building application-specific logic as a framework-independent core wrapped in a thin agent shim keeps the door open to promoting it into a shared tool later, at low cost.
- The agent/tool distinction is relative to perspective: any agent can be a tool to a higher-level orchestrator, just as any autonomous individual is simultaneously a "resource" from their organization's point of view.
