---
id: a3-05-query-transformer-user-proxy
title: "Never Trust Raw Input: The Query Transformer Agent"
week: 3
topic: "Act II: The Prompting Toolkit"
order: 5
summary: The first agent in any agentic workflow should be a query transformer that rationalizes typos, expands acronyms via RAG, standardizes named entities, and rewrites the query into a clean form — a user-proxy step that protects every downstream agent from the mess of real human language.
course: ai_agents
---

There's a principle in this week's material stated as flatly as an engineering commandment: never trust raw user input, because human-written prompts are not optimized for the agents that will process them. This sounds almost too obvious to need saying, until you notice how often agentic systems are built as if the very first thing a user types is already clean, unambiguous, and ready for a downstream reasoning agent to act on. Real user queries are typo-ridden, ambiguous, full of domain-specific acronyms nobody wrote a glossary for, and frequently reference named entities in inconsistent ways. Handing that mess directly to your most sophisticated reasoning agent is a way of guaranteeing that agent spends part of its capacity on disambiguation it was never designed to do well, instead of on the actual task.

The fix is architectural: the first agent in any pipeline should be a dedicated query transformer, whose entire job is to clean up the user's raw input before anything downstream ever sees it.

## Core intuition

A query transformer acts as a user-proxy agent: a single, focused component whose sole responsibility is producing a clean, unambiguous, well-formed version of whatever the user actually typed, so that every agent downstream of it can assume clean input as a precondition rather than having to defend against messy input independently, over and over, at every stage.

## Why it matters

Without a query transformer, the burden of handling typos, unclear acronyms, and ambiguous entities gets distributed — inconsistently — across every downstream agent in the pipeline, each of which has to make its own ad hoc judgment call about what the user probably meant. This is both wasteful (the same disambiguation problem gets solved, or half-solved, redundantly at multiple stages) and unreliable (different agents may resolve the same ambiguity differently, producing inconsistent overall behavior). Centralizing this work in one component, evaluated and improved as its own unit, converts an implicit, distributed liability into an explicit, measurable one — directly in the spirit of this week's axiom of measurement.

## Instructor framing

Have students identify, in any agentic pipeline they're designing, whether a query transformer already exists implicitly and badly (each downstream agent doing its own partial disambiguation) or exists explicitly and well (one component, one clear specification, one gold-standard dataset of its own). The implicit version is far more common in first drafts of student projects, and pointing it out is usually enough to make the architectural gap visible.

## Worked example

A user types into an internal enterprise search system: "wut r the reqs 4 the q3 opex apprvl acording 2 fin policy." Without a query transformer, this string goes directly to a retrieval and reasoning pipeline that has to simultaneously figure out this is asking about "requirements for Q3 operating expense approval according to finance policy" *and* actually answer the question — two very different kinds of work bundled into one pass, with the first kind (disambiguation) not being what the downstream reasoning agent was designed or evaluated to do well. With a query transformer in place, the four functions this week specifies run first, as their own dedicated step: query rationalization corrects the typos and abbreviations ("wut r the reqs 4" becomes "what are the requirements for"); acronym expansion detects "opex" and, using a RAG lookup against the company's internal glossary, expands it to "operating expense," and detects "fin policy" and resolves it to the specific named policy document it refers to; named entity handling standardizes "Q3" against whatever fiscal calendar convention the company actually uses (calendar Q3 versus fiscal Q3 can differ); and query rewrite assembles all of this into a single, clean, unambiguous final query — "What are the requirements for Q3 (fiscal) operating expense approval according to the Finance Policy document?" — that a downstream retrieval and reasoning agent can now process without needing to guess at any of the disambiguation the transformer already resolved.

## Math explained step by step

The case for centralizing disambiguation in one component rather than distributing it has a clean reliability argument, using the same independent-checks logic that appears elsewhere in this course's treatment of layered systems.

**Step 1 — model distributed, ad hoc disambiguation.** Suppose a pipeline has $k$ downstream agents, each independently making its own judgment call about an ambiguous term in the raw query, each with some probability $q$ of resolving it the same way a human expert would (and $q$ varies across agents, since each was designed and evaluated for a different primary task, not for disambiguation).

**Step 2 — compute the probability of pipeline-wide consistency.** For the pipeline's overall behavior to be coherent, all $k$ agents need to resolve the ambiguity the *same* way, whether or not that way is correct — the probability of all $k$ agreeing, if each resolves independently, is roughly $q^k$ in the best case (all matching the correct resolution) and can be much worse if their independent judgments diverge from each other even when each is individually plausible. This shrinks fast: even at a respectable $q = 0.85$ per agent, five independent downstream disambiguation points give at best $0.85^5 \approx 44\%$ consistent-and-correct pipeline behavior.

**Step 3 — model centralized disambiguation.** With a single query transformer resolving the ambiguity once, upstream of every downstream agent, the relevant probability is just $q_{\text{transformer}}$ — the transformer's own accuracy at this specific, dedicated task, which can be measured and improved as its own unit (its own gold-standard dataset, per the previous page) rather than being an implicit side effect of $k$ different agents' primary competencies.

**Step 4 — see why $q_{\text{transformer}}$ tends to beat the distributed alternative even before accounting for consistency.** Because the query transformer is *specialized* for exactly this task — the same specialization argument from Week 1's SLM-vs-frontier page — its dedicated accuracy $q_{\text{transformer}}$ on disambiguation tasks specifically is plausibly higher than any individual downstream agent's $q$, which was optimized for a different primary job and only incidentally has to handle disambiguation as a side effect.

## Practical pattern

1. Place a dedicated query transformer as the first stage of any agentic pipeline handling free-text user input, before any retrieval, reasoning, or tool-calling agent sees the raw query.
2. Implement its four core functions explicitly: typo/grammar rationalization, RAG-backed acronym expansion, named-entity standardization, and a final clean query rewrite.
3. Evaluate the query transformer as its own unit, with its own gold-standard dataset of messy-query-to-clean-query pairs, separate from the evaluation of downstream reasoning agents — this isolates disambiguation quality as a measurable, improvable property rather than an implicit side effect of the whole pipeline's end-to-end score.
4. When a downstream agent seems to be making inconsistent decisions about ambiguous terms, check first whether the query transformer is doing its job — the fix often belongs upstream, not in the agent where the inconsistency was observed.

## Common traps

- Skipping a dedicated query transformer and letting each downstream agent handle typos, acronyms, and ambiguous entities ad hoc, producing inconsistent pipeline-wide behavior that's hard to diagnose because the disambiguation logic is scattered.
- Building acronym expansion as a static dictionary lookup rather than a RAG-backed retrieval, missing acronyms that are context-dependent or that evolve as the company's internal vocabulary changes.
- Evaluating the query transformer only indirectly, through end-to-end pipeline accuracy, rather than directly against its own gold-standard dataset — this makes it hard to tell whether a pipeline failure originated in disambiguation or in downstream reasoning.
- Assuming a single generic prompt rewrite step is equivalent to the four explicit functions (rationalization, acronym expansion, entity handling, rewrite) — collapsing them into one vague instruction tends to under-perform a pipeline that evaluates and tunes each function separately.

## Takeaways

- Raw user input should never be trusted directly by a downstream reasoning agent — human-written queries are typo-ridden, ambiguous, and full of unexplained domain acronyms.
- A dedicated query transformer agent, acting as a user-proxy, should be the first stage of any agentic pipeline, performing rationalization, acronym expansion via RAG, named-entity standardization, and query rewrite.
- Centralizing disambiguation in one specialized, measurable component produces more consistent pipeline-wide behavior than letting $k$ downstream agents each resolve ambiguity independently.
- The query transformer should be evaluated against its own gold-standard dataset, separate from downstream reasoning agents' evaluation, to make disambiguation failures diagnosable.
