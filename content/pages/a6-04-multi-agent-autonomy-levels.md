---
id: a6-04-multi-agent-autonomy-levels
title: "Levels of Autonomy: From Operator to Observer"
week: 6
topic: "Act II: When Agents Must Talk to Other Agents"
order: 4
summary: Agentic systems exist on a graded scale of autonomy, and internal multi-agent orchestration (one process, many sub-agents) is a fundamentally different problem from external multi-agent communication across organizational boundaries.
course: ai_agents
---

"Is it an agent?" turns out to be the wrong question once you've spent a few weeks building real systems — the better question is "how much autonomy does it actually have, and over what?" A system that formats output with a bit of coded logic is not the same kind of thing as a system that proactively monitors a situation and acts on your behalf without being asked. Both get called "agents" casually. Neither comparison is useful without a scale to place them on.

This page introduces two overlapping scales the course uses: one classifying LLM *applications* by how much of the pipeline actually involves reasoning versus fixed code, and one classifying agent *autonomy* specifically, running from "does exactly what you tell it" to "watches and acts without being asked." Then it draws a second, orthogonal distinction that matters just as much once autonomy gets high enough to require coordination: whether the agents talking to each other live in the same process, or across an organizational boundary entirely.

## Core intuition

The LangChain-derived application-level scale runs from Level 1 (formatting/logic entirely hand-coded) through Level 3 (basic chaining of LLM calls) to Level 4 (routing — decomposing queries, choosing between RAG, APIs, or different LLMs based on intent) up to Levels 5-6, where the LLM itself handles output generation, planning, and reasoning — genuine autonomy. Most current LangGraph-based projects sit around Levels 5-6.

Orthogonal to this, agent autonomy in a human-facing context runs Operator (executes only what's explicitly instructed) → Collaborator (suggests actions, plans jointly with the user, then executes) → Consultant (knows the user's context and history, proactively advises) → Approver (acts on the user's behalf with granted authority) → Observer (monitors on the user's behalf, potentially acting autonomously based on what it observes, without being asked). As agents climb this ladder, the cost of miscalibrated autonomy rises sharply — an Operator that misunderstands an instruction produces one bad output; an Observer that misjudges what warrants action can take consequential steps nobody explicitly approved.

## Why it matters

Higher autonomy levels drive a structural need: as an agent moves from Operator toward Observer, the odds it needs to interact with other agents — human or artificial — increase, because higher autonomy means handling situations broader than a single, narrowly-scoped task, which in turn means coordinating with whatever other systems or people are relevant to that broader scope. This is the on-ramp to multi-agent systems, and it's worth understanding *why* the need arises before jumping into the mechanics of how agents talk to each other.

Once multi-agent coordination is needed, a second distinction becomes critical: **internal** multi-agent systems, like a LangGraph supervisor agent orchestrating sub-agents it created and wired together within the same process, are architecturally very different from **external** multi-agent systems, where agents running in separate processes — potentially at different companies, on different frameworks, on different networks entirely — need to discover each other and communicate across a trust boundary neither side fully controls.

## Instructor framing

Present the two scales (application-level, autonomy-level) as answering different questions before merging them: the application-level scale asks "how much of this pipeline is reasoning vs. fixed code," while the autonomy-level scale asks "how much license does this reasoning have to act without checking in." A system can be high on one axis and low on the other — a Level 6 application (heavy LLM-driven reasoning) that's still purely an Operator (only acts on explicit instruction) is a coherent, common design, and students should be able to place a system they've built on both axes independently rather than treating "how agentic is it" as a single number.

## Worked example

Consider a research-assistant agent evolving over a product's lifetime. Version one is an Operator: a user asks a specific question, the agent retrieves and answers, nothing more — Level 4-5 on the application scale, since it's doing some routing and reasoning but strictly on-demand.

Version two becomes a Collaborator: given a broad research goal, it proposes a research plan, checks with the user before proceeding, then executes — still fundamentally reactive, but now planning jointly rather than just answering.

Version three becomes a Consultant: it retains context across sessions, notices when new information relevant to a standing user interest appears, and proactively surfaces it without being explicitly asked each time — Level 5-6 on the application scale, since it's now doing autonomous planning about *when* to act, not just *how*.

At this point, the research assistant plausibly needs to talk to other agents: an internal summarization sub-agent it spawns and controls (internal multi-agent, single process, the LangGraph-supervisor pattern), and potentially an external agent at a different organization — a partner company's document-retrieval agent it needs to query for licensed content (external multi-agent, crossing a trust and process boundary the internal case never has to deal with).

## Math explained step by step

Model the coordination-need growth as autonomy increases, since "higher autonomy needs more coordination" deserves more than intuition.

**Step 1 — define scope breadth as a function of autonomy level.** Let $\sigma$ be the breadth of situations an agent at a given autonomy level is expected to handle without new explicit instruction. An Operator has $\sigma \approx 1$ (handles exactly the one instructed task); an Observer has $\sigma \gg 1$ (monitors and potentially acts across an open-ended range of situations it wasn't specifically told to watch for).

**Step 2 — relate scope breadth to the number of relevant external systems.** As $\sigma$ grows, the number of distinct systems, data sources, or other agents whose state might be relevant to "should I act right now" grows at least proportionally — an Observer watching a broad domain needs visibility into more of that domain's moving parts than an Operator executing one narrow, fully-specified task ever does.

**Step 3 — coordination cost as a function of relevant-system count.** If coordinating with $m$ other systems/agents requires pairwise discovery and communication setup, the naive coordination cost scales as $O(m)$ per new system added, or $O(m^2)$ if those systems also need to coordinate with each other rather than just with the central agent — this is exactly the argument for centralized discovery mechanisms (a broker or DNS-like registry) once $m$ grows large, since they convert the $O(m^2)$ pairwise-integration cost into an $O(m)$ registration-and-lookup cost.

**Step 4 — the practical threshold.** For low-autonomy agents (Operator, Collaborator) with small $\sigma$, ad hoc, hand-wired coordination with one or two known systems is manageable — an internal multi-agent setup within a single LangGraph process suffices. For high-autonomy agents (Consultant, Approver, Observer) with large $\sigma$, the coordination burden crosses into territory where discovery mechanisms and standardized cross-boundary protocols (the next page's topic) stop being nice-to-haves and become structurally necessary.

## Practical pattern

Placing a system correctly on both scales before building its coordination layer:

1. rate the system honestly on the application-level scale (how much genuine reasoning vs. fixed code) and the autonomy-level scale (Operator through Observer) separately — resist collapsing these into a single "how agentic" judgment;
2. estimate scope breadth $\sigma$ directly: how many distinct situations, without new instruction, is this agent expected to correctly handle? A large, open-ended answer is the signal that multi-agent coordination needs are coming, even if the system doesn't need it on day one;
3. for internal multi-agent needs (sub-agents the system itself spawns and controls), a single-process supervisor pattern is usually sufficient and avoids unnecessary cross-boundary complexity;
4. for external multi-agent needs (agents outside your process, organization, or trust boundary), plan for discovery and standardized communication from the start, rather than hand-wiring point-to-point integrations that won't generalize as $m$ grows;
5. revisit the autonomy rating as a system evolves — a system that starts as an Operator and gradually gains Consultant- or Observer-like behavior through incremental feature additions needs its coordination architecture reassessed at each jump, not just at initial design time.

## Common traps

- treating "agent" as binary rather than placing a system on both the application-level and autonomy-level scales, which obscures real differences between systems that get the same casual label;
- building high-autonomy (Consultant/Observer-level) behavior without recognizing the coordination burden that comes with the resulting scope breadth, leading to systems that "act autonomously" on stale or incomplete visibility into relevant external state;
- defaulting to hand-wired, pairwise integrations for external multi-agent coordination because it's the fastest thing to build, without recognizing that this cost scales poorly ($O(m)$ or worse per new integration) compared to investing in a discovery mechanism once $m$ is expected to grow;
- conflating internal multi-agent orchestration (a supervisor spawning sub-agents in one process) with external multi-agent communication (crossing organizational and trust boundaries) — the two have almost nothing in common mechanically, despite both being called "multi-agent."

## Takeaways

- Two independent scales matter for classifying agentic systems: how much genuine reasoning versus fixed code the pipeline involves (application level), and how much license the system has to act without checking in (autonomy level, Operator through Observer).
- As autonomy increases, the breadth of situations an agent must handle without new instruction grows, which drives a structural need for coordination with other systems and agents — this is the on-ramp from single-agent design into multi-agent architecture.
- Internal multi-agent systems (single process, one team's supervisor pattern) and external multi-agent systems (crossing organizational or trust boundaries) are fundamentally different engineering problems, and recognizing which one you actually have determines whether hand-wired integration is sufficient or a discovery mechanism is structurally necessary.
