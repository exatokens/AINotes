---
id: a4-03-tool-maximalist-mcp
title: "The Tool-Maximalist Perspective: Intelligence Is Not in the Model Alone"
week: 4
topic: "Act II: Architecting Reliable Agents"
order: 3
summary: Under the tool-maximalist view, an agent's intelligence emerges from the ecosystem of reasoner plus tools, not from the model's weights in isolation — and MCP is the protocol that lets tools describe their own capabilities richly enough for an agent to reason about what's possible before deciding how to act.
course: ai_agents
---

There's a perspective on agentic intelligence this week revisits from a genuinely deep angle, and it's worth sitting with because it reframes a question students keep asking in slightly different forms all bootcamp: "is the intelligence in the model, or somewhere else?" The tool-maximalist perspective gives a specific, committed answer: it rejects "the fantasy of the self-sufficient model" and claims instead that an agent's intelligence is a *system property*, emerging from the combination of a reasoning core and the tools it's connected to — not a property sealed inside the model's weights.

Under this view, the language model is not the mind. It's the medium — a semantic field through which plans get formed, delegated, and revised — while the surrounding network of tools provides the mechanical precision and factual grounding pure language modeling lacks on its own. An agent's effective intelligence, on this account, is a function of the diversity and depth of the tools it can reach, not primarily a function of how large or capable its base model is.

## Core intuition

Reasoning alone has limited reach; the tool-maximalist view holds that what actually defines an agent's intelligence is the scope, fluency, and adaptability of the external world it can act upon — not the sophistication of its internal logic in isolation. An agent doesn't merely call tools it already knows about; through good tool documentation, it reasons *about capability itself*, discovering what becomes possible given a specific goal before deciding how to proceed.

## Why it matters

This directly explains why the documentation-quality argument from Week 2 (the "environment fencing and tool documentation" page) isn't a minor operational detail — under the tool-maximalist view, it's central to the agent's actual intelligence. If a tool's description doesn't let the agent grasp its potential relative to the current goal, that tool's contribution to the system's overall intelligence is effectively wasted, no matter how capable the underlying reasoning model is. This also explains why MCP is described in almost utopian terms this bootcamp: as a "universal grammar of actions" rather than merely a convenient API standard — because standardizing how tools describe their own capability is standardizing the very substrate this perspective claims intelligence actually lives in.

## Instructor framing

Push students on the epistemological stance explicitly, because it has real design consequences: if you believe intelligence lives mostly in the model, you invest primarily in bigger models and better prompts. If you believe intelligence is a system property emerging from agent-plus-tools, you invest at least as heavily in tool design, tool documentation, and tool diversity — and this week's material is explicit that a search tool doing its own internal self-consistency check ("does it make sense that a laptop costs £300? do I trust this result?") is *itself* a form of agentic reasoning, distributed into the tool rather than concentrated in the central model. Cognition, on this view, is genuinely distributed across the ecosystem, not merely delegated by it.

## Worked example

Consider a search tool wired into an agent through MCP. A naive integration treats the tool as a dumb pipe: call the search API, return whatever comes back, let the central reasoning model sort out whether to trust it. Under the tool-maximalist design this week describes, the search tool itself carries some of the reasoning burden — checking internally whether a returned price for a laptop is plausible, whether a source looks credible, whether the result should be flagged as uncertain before it's even handed back to the orchestrating agent. This is "distributed cognition" in a very literal sense: intelligence about *trustworthiness of a search result* lives in the tool, not the central model, and the central model's job becomes coordinating and synthesizing across multiple such semi-intelligent components rather than doing all the epistemic work itself. Multiply this pattern across many tools — a text-to-SQL tool that validates its own generated query against a schema before returning it, a document-retrieval tool that checks its own result's relevance before surfacing it — and the system's overall reliability comes from the sum of these distributed checks, not from one central model reasoning perfectly about everything.

## Math explained step by step

The tool-maximalist claim — "an agent's IQ is a function of the diversity and depth of its connected tools" — can be given a concrete combinatorial shape, connecting it to the MCP integration-cost argument from Week 1.

**Step 1 — define reachable goal-space as a function of tool diversity.** Let $T$ be the set of tools an agent can access, and let $\text{Reach}(T)$ be the space of distinct goals or sub-goals the agent can actually accomplish using some composition of tools in $T$. A model with brilliant reasoning but $T = \emptyset$ (no tools) has $\text{Reach}(T) = \emptyset$ for any goal requiring real-world action or fresh information — its intelligence, however deep, has nowhere to land.

**Step 2 — model diminishing but genuine returns to adding tools.** As $|T|$ grows, $\text{Reach}(T)$ grows, but not purely additively — some new tools open genuinely new goal categories (adding a payment-processing tool opens an entire class of transactional goals previously unreachable), while others merely duplicate existing reach (a second, overlapping search tool adds little to $\text{Reach}(T)$ while adding the overlap-driven selection-confusion cost from Week 2's tool-documentation page).

**Step 3 — separate tool *count* from tool *documentation quality* as independent multipliers.** Define effective reach as $\text{Reach}_{\text{eff}}(T) = \text{Reach}(T) \cdot q_{\text{doc}}$, where $q_{\text{doc}} \in [0,1]$ is the average quality of tool self-description across $T$ — a large, diverse tool set with poor documentation ($q_{\text{doc}}$ low) yields much lower effective reach than the raw $\text{Reach}(T)$ would suggest, because the agent cannot reliably discover or correctly invoke capability it can't clearly reason about. This formalizes why documentation quality and tool diversity are both necessary and neither is sufficient alone.

**Step 4 — connect this back to MCP's integration-cost savings.** Recall from Week 1 that a shared protocol converts tool-integration cost from $O(mn)$ (applications times tools) to $O(m+n)$. Combined with Steps 1-3, MCP doesn't just make integration cheaper — it directly raises $q_{\text{doc}}$ system-wide, since a protocol that *requires* self-describing schemas, parameters, and affordances forces a documentation floor that ad hoc bespoke integrations never enforced. Cheaper integration and better-forced documentation compound: MCP adoption plausibly raises $\text{Reach}_{\text{eff}}(T)$ through both terms in the formula simultaneously.

## Practical pattern

1. When evaluating whether to invest in a bigger reasoning model versus a richer, better-documented tool ecosystem, remember the tool-maximalist claim: for many enterprise tasks, effective intelligence gains from expanding $\text{Reach}_{\text{eff}}(T)$ (more, better-documented tools) may outpace gains from a larger base model alone.
2. Design tools to carry some of their own reasoning burden where possible — a search tool that self-assesses result plausibility, a SQL-generation tool that validates its own output against a schema — rather than pushing all epistemic work to the central orchestrating agent.
3. Write tool descriptions specifically to let an agent reason about *capability*, not just *invocation syntax* — describe what becomes possible given a goal, not merely the function signature, so the agent can discover relevant tools it wasn't explicitly told to look for.
4. Treat MCP adoption as a documentation-quality intervention as much as an integration-cost intervention — the protocol's requirement for self-describing schemas is doing real work on $q_{\text{doc}}$, not just on integration effort.

## Common traps

- Investing exclusively in larger, more capable base models while under-investing in tool diversity and documentation quality, missing that effective intelligence under the tool-maximalist view is bounded by both factors jointly.
- Adding tools purely to increase raw count ($|T|$) without checking whether they genuinely expand $\text{Reach}(T)$ or merely duplicate existing overlapping capability, which mainly adds selection confusion rather than genuine reach.
- Writing tool integrations (even MCP-compliant ones) with minimal, purely syntactic descriptions that satisfy the protocol technically but don't actually let an agent reason about the tool's potential relative to a goal — technically compliant but practically low $q_{\text{doc}}$.
- Concentrating all validation and self-checking logic in the central orchestrating agent, missing the distributed-cognition opportunity to push some of that burden into the tools themselves, closer to where the relevant domain knowledge actually lives.

## Takeaways

- The tool-maximalist perspective holds that an agent's intelligence emerges from the ecosystem of reasoner plus tools, not from the model's weights in isolation — a view that rejects "the fantasy of the self-sufficient model."
- MCP functions as a universal, self-describing interface for tools, letting an agent reason about capability before deciding how to act, and enforcing a documentation floor that ad hoc integrations never guaranteed.
- Effective agent intelligence can be modeled as reachable goal-space multiplied by average tool-documentation quality — both tool diversity and documentation quality are necessary, and neither alone is sufficient.
- Distributed cognition — pushing some reasoning and self-validation into the tools themselves, not only the central model — is a genuine architectural strategy for reliability, not just a metaphor.
