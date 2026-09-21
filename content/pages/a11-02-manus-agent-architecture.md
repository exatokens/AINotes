---
id: a11-02-manus-agent-architecture
title: "Inside Manus: CodeAct, the Sandbox, and the Agent Loop"
week: 11
topic: "Act I: Inside Manus"
order: 2
summary: Manus is not a proprietary model but an orchestration layer around frontier LLMs, made powerful by three architectural choices — executable code as the action format, a full cloud sandbox, and a strictly one-action-per-iteration control loop.
course: ai_agents
---

When independent researchers reverse-engineered Manus from its leaked system prompt and public statements, the finding that mattered most was not any secret proprietary model — there wasn't one. Manus's own chief scientist confirmed its reasoning engine was Anthropic's Claude (initially 3.5 Sonnet, later 3.7), supplemented by fine-tuned versions of Alibaba's Qwen. The "magic" was not in a bespoke foundation model. It was in the surrounding architecture: how the agent loop was structured, how the model was given the ability to actually *act* rather than only converse, and how state was managed across a task that could run for dozens of steps in a cloud sandbox.

This page reconstructs that architecture from the technical investigation into Manus, because the pattern it describes — a capable frontier model wrapped in a disciplined loop, a sandboxed execution environment, and externalized memory — is close to the reference architecture for any serious autonomous agent built today, whether or not it uses Manus's specific choices.

## Core intuition

Manus's tool-use mechanism is built on **CodeAct**: rather than emitting a fixed, rigid action format like `SEARCH(query)` or a narrow JSON schema, the model generates short, executable Python scripts as its actions. The 2024 CodeAct research this is based on found that agents producing executable code for actions achieve significantly higher success rates on complex tool-using tasks than agents restricted to simple textual tool calls — code can combine multiple tools and conditional logic in one action, draw on arbitrary libraries, and be iteratively debugged by the agent itself when it fails.

This runs inside a genuine **cloud sandbox**: a full Ubuntu Linux environment with internet access, shell (with sudo), a controllable web browser, a file system, and Python/Node interpreters — a virtual computing environment, not a text box. Because this runs server-side, Manus continues working even if the user's device is off, unlike browser-resident agents.

## Why it matters

The agent loop itself is deliberately narrow: **analyze** the current state from an event stream of recent interactions, **plan or select** one action, **execute** it in the sandbox, **observe** the result and append it to the event stream — repeat until the task is judged complete. Crucially, the design limits the agent to exactly **one tool action per iteration**; it must await each result before deciding the next step. This is a safety-and-controllability decision, not a performance one: it prevents the model from running away with an unchecked, cascading sequence of operations, and gives both the system and the user a monitorable checkpoint after every single action.

## Instructor framing

Draw a direct line from this page's CodeAct discussion back to the previous page's KV-cache and masking rules — CodeAct actions still have to be serialized into the context the model reads, so every context-engineering discipline from the first Manus page (stable prefixes, append-only history, masking over removing tools) applies unchanged to a CodeAct-based agent. Architecture (this page) and context engineering (the previous page) are not separate concerns; they are the same system viewed from two angles, and a strong agent needs both done well simultaneously.

## Worked example

Consider Manus performing a weather lookup. Rather than a rigid built-in `Weather()` function, the model generates Python code that imports a helper library and calls a weather API client directly — something like `import sys; sys.path.append('/opt/.manus/.sandbox-runtime'); ...` followed by a call to the appropriate client and a print of the result. The sandbox executes this code and returns its output (or its error) as the next observation. If the code errors, Manus can read the traceback and iteratively revise the code and retry — essentially debugging itself — which is precisely the flexibility a rigid, fixed-schema action format would not afford.

Task decomposition follows a similar externalize-and-check pattern. A dedicated **Planner module** breaks a high-level goal into an ordered, numbered list of steps injected into context as a "Plan" event — for a data-visualization request, perhaps: gather data, clean data, generate plot, save and send. The agent refers back to this plan every iteration and knows it must complete every step before finishing, and can re-plan if the task changes mid-stream. A **Knowledge module** and a **Datasource module** supply domain best-practices and authoritative API access respectively, so the agent isn't relying purely on parametric memory — the developers describe this directly as retrieval-augmented generation folded into the agent's normal operation, not a separate mode.

## Math explained step by step

Quantify why the strict one-action-per-iteration rule and the sandboxed error-recovery loop matter for reliability, using a simple compounding-probability model.

**Step 1 — model per-step reliability.** Suppose each individual tool-call step in a multi-step task succeeds independently with probability $p$ (say $p = 0.9$ for a well-engineered action). For a task requiring $n$ sequential steps with no error recovery, the probability the *whole* task completes without any single-step failure is $p^n$.

**Step 2 — see how this collapses for realistic $n$.** At $p = 0.9$ and a Manus-scale task of $n = 50$ tool calls, $p^n = 0.9^{50} \approx 0.005$ — a task with no error-recovery mechanism at all would succeed essentially never, even though each individual step is quite reliable in isolation.

**Step 3 — see what per-step observation and retry buys back.** If each failed step can be detected (via the observation returned by the sandbox) and retried up to $k$ times independently, the effective per-step success probability rises to $1 - (1-p)^k$. At $p = 0.9$ and $k = 2$ retries, effective per-step reliability rises to $1 - 0.1^2 = 0.99$, and the whole-task probability becomes $0.99^{50} \approx 0.605$ — over a hundredfold improvement in task-level reliability purely from the ability to observe a failure and retry it, rather than needing every step to succeed blind on the first attempt.

**Step 4 — the architectural conclusion.** This is the quantitative case for the one-action-per-iteration, observe-then-decide loop: it is precisely what makes per-step retry and error recovery possible at all. A design that instead let the model emit a long, unchecked cascade of actions in one shot would forfeit the ability to detect and retry failures mid-sequence, and the $p^n$ regime — vanishing task-level reliability at realistic task lengths — would dominate.

## Practical pattern

1. give the agent an executable action format (code, not a narrow fixed schema) whenever tasks might require composing multiple tools or conditional logic in one action — this is the CodeAct lesson, and it measurably improves complex tool-use success rates;
2. run the agent inside a genuine sandboxed environment (containerized Linux, browser automation, file system) rather than a restricted tool API, so it can recover from errors the way a human operator would — by reading the error and adjusting;
3. enforce a strict one-action-per-iteration control loop with mandatory observation before the next decision — the reliability math above shows this is not merely cautious engineering, it is close to a prerequisite for acceptable task-level success rates at realistic task lengths;
4. externalize planning into an explicit, inspectable artifact (a numbered plan, injected into context as its own event) rather than relying on the model to silently track task decomposition in its own reasoning — this both improves reliability and gives you and the user a way to audit progress.

## Common traps

- restricting an agent to a small, fixed set of narrowly-typed tool calls when the task space benefits from composability — this is exactly the ceiling CodeAct's executable-code approach was built to remove;
- allowing an agent to chain multiple actions per loop iteration without an observation checkpoint in between, which both forfeits the retry-driven reliability gains shown above and makes runaway, unchecked action sequences possible;
- treating the underlying frontier model as the entire "product," when for Manus the differentiating engineering was overwhelmingly in the loop, the sandbox, and the planning/memory scaffolding around a model it did not itself train;
- omitting an explicit, inspectable plan artifact and relying on the model to hold task decomposition purely in its own working context, which becomes fragile exactly as tasks grow long enough to need a plan in the first place.

## Takeaways

- Manus's core engine is an off-the-shelf frontier model (Claude, supplemented by fine-tuned Qwen); its differentiation is architectural — CodeAct-style executable actions, a genuine cloud sandbox, and a disciplined control loop.
- CodeAct's executable-code action format outperforms rigid, fixed-schema tool calls on complex, multi-tool tasks because code can compose logic and be self-debugged by the agent on failure.
- A strict one-action-per-iteration, observe-before-deciding loop is not just a safety measure — it is close to mathematically necessary for acceptable task-level reliability once tasks run to dozens of sequential steps, because uncontrolled step-chaining forfeits the retry-based reliability gains that make long tasks tractable at all.
- Explicit, externalized planning (a numbered plan injected as its own context event) and retrieval-augmented knowledge and data modules keep a long-running agent both auditable and grounded, rather than relying purely on the model's own working memory and parametric knowledge.
