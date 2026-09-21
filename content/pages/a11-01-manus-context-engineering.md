---
id: a11-01-manus-context-engineering
title: "Context Engineering for AI Agents: Lessons from Building Manus"
week: 11
topic: "Act I: Inside Manus"
order: 1
summary: Manus bet on context engineering over training a custom model, and its six hard-won rules — cache design, masking over removal, filesystem-as-memory, recitation, keeping failures visible, and avoiding few-shot ruts — are load-bearing production lessons, not style preferences.
course: ai_agents
---

At the start of the Manus project, the team faced a decision every serious agent builder eventually confronts: train an end-to-end agentic model from open-source foundations, or build entirely on top of the in-context learning ability of an existing frontier model. Manus's founder had already lived the alternative in a previous startup — training bespoke models from scratch for open information extraction and semantic search, with iteration cycles measured in weeks, only to watch those models become irrelevant overnight the moment GPT-3 and Flan-T5 arrived. That was the "bitter lesson" that decided Manus's bet: build on context engineering, ship improvements in hours rather than weeks, and stay orthogonal to whichever model is currently best — be the boat that rises with the tide, not the pillar stuck to the seabed.

What followed was not a single clever prompt but a genuinely experimental science, arrived at through four full rewrites of the agent framework — a process the Manus team affectionately calls "Stochastic Graduate Descent": architecture searching, prompt fiddling, and empirical guesswork, inelegant but effective. This page works through the resulting local optima, because each one generalizes far past Manus itself to any agent built the same way — as a loop of tool calls over a frontier model's context window.

## Core intuition

An agent loop, stripped to its mechanics, looks the same regardless of what task it performs: receive input, select an action from a predefined space based on current context, execute that action in an environment to produce an observation, append both to context, repeat. Every iteration the context grows, while the output — typically a short, structured function call — stays roughly constant in size. This makes the ratio between "tokens read" and "tokens written" wildly skewed compared to a chatbot: Manus's average input-to-output token ratio runs around 100:1. Context engineering, in this light, is not a stylistic add-on to agent building — it *is* the majority of the engineering surface area, because nearly every token an agent processes is context it accumulated, not context a user typed.

## Why it matters

Because of that skew, the single most consequential metric for a production agent is its **KV-cache hit rate** — it directly determines both latency and cost. Contexts sharing an identical prefix can reuse cached key-value computations, drastically cutting time-to-first-token and inference cost, whether self-hosted or called through an API. The financial stakes are not subtle: with Claude Sonnet, cached input tokens cost roughly $0.30 per million tokens versus $3 per million uncached — a 10x difference, applied to every single one of the roughly 100 context tokens an agent reads for every token it writes.

## Instructor framing

Present the KV-cache discussion first and insist students internalize *why* an agent's 100:1 read-to-write ratio makes caching the dominant cost lever, before moving to any of Manus's other five rules — every subsequent rule in this page (mask-don't-remove, filesystem-as-context, recitation, keeping failures visible, avoiding few-shot ruts) is best understood as a corollary of protecting that cache hit rate or of managing context growth without destroying it. A student who has internalized the 100:1 ratio will correctly predict most of Manus's specific engineering choices before being told them.

## Worked example

Three concrete practices protect the KV-cache hit rate. First, keep the prompt prefix stable — because LLMs are autoregressive, a single-token difference invalidates the cache from that point forward, so a common and costly mistake is putting a to-the-second timestamp at the start of a system prompt: it lets the model report the current time, but it silently kills the cache hit rate for every subsequent request, since that prefix is now different every second. Second, make context strictly append-only, never rewriting past actions or observations, and ensure serialization is deterministic — many JSON libraries don't guarantee stable key ordering, which can invisibly break the cache even when the *logical* content hasn't changed. Third, mark cache breakpoints explicitly where a provider requires it, accounting for cache expiration and, at minimum, always placing a breakpoint at the end of the system prompt.

A second, related engineering choice is masking rather than removing tools as the action space grows. As an agent gains capabilities — accelerated by the popularity of MCP, where users can plug in hundreds of unfamiliar tools — a natural instinct is to dynamically load and unload tool definitions mid-task, RAG-style. Manus tried this and rejected it, for two concrete reasons: tool definitions typically sit near the front of the serialized context, so any change to them invalidates the KV-cache for every subsequent action and observation; and when prior actions in context still reference tools no longer defined in the current context, the model gets confused and, without constrained decoding, produces schema violations or hallucinated actions. Manus's fix is a context-aware state machine that masks token logits during decoding — using consistent action-name prefixes (`browser_`, `shell_`) so a whole family of tools can be enabled or disabled by masking without ever touching the tool definitions themselves, preserving the cache.

## Math explained step by step

Quantify the cache-hit-rate economics directly, since "10x difference" is a number worth deriving rather than taking on faith.

**Step 1 — set up per-request token cost.** For an agent averaging $r$ input tokens read per output token written (Manus reports $r \approx 100$), and a task requiring $m$ tool-call iterations, total input tokens processed over the task is roughly $\sum_{i=1}^{m} r \cdot i$ if context grows linearly by appending each prior action-observation pair (a triangular sum, since each iteration re-reads all prior context).

**Step 2 — apply the cached-versus-uncached price difference.** At Claude Sonnet's reported rates, uncached input costs $\$3$/MTok and cached input costs $\$0.30$/MTok — a 10x multiplier. If the prefix-stability rule is violated even once mid-task (say, a timestamp changes every iteration), every subsequent iteration's entire growing context is uncached, multiplying the *already-growing* triangular token sum by 10x rather than 1x.

**Step 3 — see why this compounds with task length.** For a task with Manus's reported average of about 50 tool calls, the triangular-sum context-token total is on the order of $r \times \frac{m(m+1)}{2} \approx 100 \times \frac{50 \times 51}{2} \approx 127{,}500$ input tokens processed across the task. At a broken cache (10x the per-token price), this single task's input cost is roughly ten times what a cache-stable implementation would pay — for identical model behavior, purely as a consequence of one avoidable prefix-stability bug.

**Step 4 — the design implication.** Because cache breakage multiplies a quantity that is *already* growing quadratically-ish with task length (the triangular sum), the cost of a cache-breaking bug is not a fixed overhead — it compounds precisely on the longest, most complex, most valuable tasks an agent runs. This is why Manus treats KV-cache hit rate as the single most important production metric rather than one optimization among many.

## Practical pattern

1. audit your system prompt for anything that changes between otherwise-identical requests — timestamps, request IDs, or non-deterministically-serialized JSON are the most common silent cache-killers;
2. make your agent's context append-only by construction — never edit or delete a past action or observation in place, since even a semantically-neutral edit invalidates every cached token after it;
3. when your action space needs to shrink or grow dynamically, mask candidate actions via logit constraints (response prefill, in the Hermes-style Auto/Required/Specified modes) rather than adding or removing tool definitions from the context;
4. externalize large or bulky observations (web pages, PDFs, documents) to the filesystem the moment they're no longer immediately needed, keeping only a restorable pointer (a URL, a file path) in the live context — the next page in this pair, on Manus's overall architecture, develops this filesystem-as-memory pattern further.

## Common traps

- putting any high-precision, frequently-changing value (a timestamp, a request counter) at the front of a system prompt, unaware that it silently destroys the cache hit rate for every subsequent turn;
- dynamically adding or removing tool definitions mid-task to keep the action space "clean," not realizing this both breaks the cache and risks the model referencing now-undefined tools from earlier context, producing hallucinated actions;
- assuming JSON serialization is automatically deterministic across a codebase's various libraries, when unstable key ordering is a common and easy-to-miss source of intermittent cache invalidation;
- treating context engineering as a one-time setup task rather than the ongoing, dominant cost lever it is for any agent with a high context-read-to-output-write ratio.

## Takeaways

- Manus deliberately chose context engineering over training a bespoke model, betting on iteration speed (hours, not weeks) and staying orthogonal to whichever underlying model is currently best.
- KV-cache hit rate is the single most consequential metric for a production agent's latency and cost, because agent loops read roughly 100 tokens of accumulated context for every token they write.
- Protect the cache by keeping prompt prefixes stable, making context strictly append-only with deterministic serialization, and marking explicit cache breakpoints where needed.
- Prefer masking token logits over dynamically adding or removing tool definitions when the action space needs to change mid-task — removal breaks the cache and risks the model referencing tools no longer defined.
