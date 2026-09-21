---
id: a3-07-ai-assisted-coding-guardrails
title: "The Middle Path: AI-Assisted Coding Without Vibe Coding"
week: 3
topic: "Act III: Economics and Engineering Discipline"
order: 7
summary: Between complete vibe coding and refusing to use AI code generators at all lies a disciplined middle path — Cursor Rules that encode a team's standards as persistent, machine-readable constraints, converting an AI code generator into a reliable, opinionated assistant.
course: ai_agents
---

Building agents requires writing a lot of ordinary software around them, and this week closes with a practical question that has nothing to do with prompting agents and everything to do with building them: how should a team actually use an AI coding assistant like Cursor day to day? The material identifies two extremes, both bad. One is complete vibe coding — describing what you want in English and accepting whatever code comes back, which tends to produce large, outdated, hard-to-debug code using a mishmash of libraries, because the median age of publicly available training code is roughly a decade old and coding assistants inherit those dated habits by default. The other extreme is the Luddite refusal to use AI-assisted coding at all, discarding a genuinely useful productivity tool out of distrust.

The middle path — the one this week actually recommends — is AI-assisted coding constrained by explicit, persistent rules that encode a team's actual engineering standards, so the assistant stops defaulting to whatever pattern was statistically common in its training data and starts following the specific conventions this project has decided on.

## Core intuition

An AI code generator without constraints defaults to the statistical average of its training distribution — dated libraries, generic exception handling, inconsistent style — because it has no way to know your team's specific preferences unless you tell it, every time, in every conversation. Cursor Rules (or the equivalent in any AI-enabled IDE) solve this by encoding those preferences once, persistently, as a project-level specification the assistant reads automatically, rather than requiring you to restate your standards in every single prompt.

## Why it matters

Repeating the same corrections prompt after prompt — "please use type hints," "please add logging," "please don't put this in `__init__.py`" — is not just tedious, it's a sign the actual specification (the team's engineering standards) is living nowhere durable. The moment those standards are written down as a persistent rules file, the AI assistant stops needing to be told the same thing over and over, and — just as importantly — the standards themselves become an artifact the team can review, version, and improve, rather than tacit knowledge that lives only in each developer's head.

## Instructor framing

Connect this directly back to the gold-standard-dataset argument earlier this week: a Cursor Rules file is, structurally, the same move as a gold-standard dataset — it converts an implicit, inconsistently-applied standard (what "good code" means to this team) into an explicit, persistent, machine-readable specification that a stochastic system (the coding assistant) can be measured and corrected against. The domains differ (code style versus agent behavior), but the underlying discipline — externalize the specification, don't leave it as a vague, restated-every-time preference — is the same discipline this entire week has been building toward.

## Worked example

Walk through the PDF-downloader project exactly as it unfolds in this week's material, because the failure-then-fix sequence is instructive. Prompt #1 — "write a simple function that downloads a PDF from a URL, call it `download`" — produces code, but Cursor places it directly inside `__init__.py`, which is structurally wrong; nothing in the prompt specified otherwise, so the assistant defaulted to the path of least resistance. Prompt #2 asks for the code to be moved into its own file, `download.py`, and it complies, but the resulting code still throws generic exceptions, has no logging, and has no retry logic — again, nothing in the prompt ruled these out, so nothing ruled them in either. Rather than continuing to issue one-off corrections indefinitely, the fix is a Cursor Rules file — a persistent `.mdc` markdown file specifying role and persona ("you are a senior Python ML engineer... prioritize efficient, maintainable code"), code style conventions (use `uv` for dependency management, Google-style docstrings, strict type annotations, `loguru` for logging), cognitive-complexity limits (maximum nesting depth of two levels), documentation requirements (detailed Markdown docs with Mermaid diagrams where appropriate), and contextual-awareness requirements (read the entire codebase before making changes, to avoid duplicating existing functionality). Prompt #3 — "apply all of my cursor rules to this project, then review again and ensure compliance" — now produces a systematic pass that fixes the earlier issues in one step, because the standards it's checking against are no longer implicit.

## Math explained step by step

The economics of writing a persistent rules file versus repeating corrections prompt-by-prompt is a straightforward amortization argument, worth making explicit since "write the rules file once" is easy to under-value against the immediate friction of writing it.

**Step 1 — define the per-prompt correction cost.** Let $c$ be the cost (developer time, tokens, review effort) of manually restating a given standard — "add type hints," say — in one prompt, and let $f$ be the frequency with which that standard needs restating across a project's lifetime if it's never written down persistently.

**Step 2 — define the rules-file cost.** Let $R$ be the one-time cost of writing that standard into a persistent Cursor Rules file, typically higher than a single prompt's restatement cost ($R > c$), since it requires being precise and complete enough to apply automatically without further clarification.

**Step 3 — find the break-even point.** Total cost without a rules file, over $f$ restatements, is $c \cdot f$. Total cost with a rules file is $R$ (paid once) plus a small per-use overhead $\epsilon$ for the assistant to read and apply it each time (negligible compared to $c$, since it's automatic rather than requiring developer attention). The rules file wins whenever $c \cdot f > R$ — and since most real engineering standards (type hints, logging conventions, exception handling patterns) get invoked dozens or hundreds of times across a project's life, $f$ is almost always large enough to clear this bar quickly.

**Step 4 — see the compounding benefit across a team, not just a single developer.** $f$ in Step 1 should really be summed across every developer on the project who would otherwise separately restate the same standard in their own prompts — a rules file pays for itself once per project, while the restatement cost without one is paid independently, repeatedly, by every team member. This is the same amortization logic as the query transformer page: centralize a repeated cost once, rather than paying it distributed and redundantly.

## Practical pattern

1. Write Cursor Rules (or your IDE's equivalent persistent-instruction mechanism) as soon as a project starts, covering role/persona, code style and library conventions, complexity limits, documentation requirements, and contextual-awareness expectations — don't wait until you've manually corrected the same issue three times.
2. Keep rules in multiple, separate files by concern (style, architecture, testing) rather than one monolithic file — this improves modularity and makes individual rule sets easier to review and update independently.
3. Be deliberate about which rules apply "always" versus only when explicitly invoked — always-applied rules consume context budget (and, on metered plans, real cost) on every single request, so reserve "always" for genuinely universal standards.
4. Establish documentation generation (e.g., `mkdocs`) and a custom exception hierarchy with structured context as standards from the very first commit, not as a later cleanup pass — both compound in value the longer a codebase lives.

## Common traps

- Complete vibe coding: accepting AI-generated code wholesale without review, inheriting the training data's dated conventions (older libraries, generic exception handling) into a new codebase by default.
- The Luddite trap: refusing AI-assisted coding entirely, forfeiting a genuine productivity tool because of a small number of bad early experiences with unconstrained generation.
- Repeating the same manual correction across many prompts and many developers rather than writing it once into a persistent rules file — this is the code equivalent of the "raw user input" problem the query transformer page addresses.
- Marking too many rules as "always apply" on a metered coding-assistant plan, burning through usage budget faster than necessary for rules that only a subset of requests actually need.

## Takeaways

- Complete vibe coding and complete refusal to use AI coding tools are both worse than a disciplined middle path built on explicit, persistent standards.
- Cursor Rules (or equivalent) convert implicit, repeatedly-restated engineering standards into a durable, machine-readable specification the assistant applies automatically.
- The amortization math favors writing standards down early and explicitly: the one-time cost of a rules file is almost always smaller than the cumulative cost of restating the same correction across many prompts and many developers.
- This is the same underlying discipline as the gold-standard dataset and the query transformer earlier this week — externalize a repeated, implicit judgment into an explicit, persistent, reviewable artifact.
