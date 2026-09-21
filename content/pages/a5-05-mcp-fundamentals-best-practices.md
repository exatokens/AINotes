---
id: a5-05-mcp-fundamentals-best-practices
title: "MCP: Making Tools Legible to a Model"
week: 5
topic: "Act III: From Prototype to Production — MCP Architecture"
order: 5
summary: The Model Context Protocol standardizes how a tool describes itself so an LLM-backed agent can discover, understand, and safely invoke it — and its reach extends past software into physical systems.
course: ai_agents
---

An agent can only use a tool it can understand. That sounds obvious, but it's the entire reason the Model Context Protocol exists, and it explains why "just call a REST API" was never a satisfying answer for agentic systems. A REST endpoint has documentation, but that documentation lives somewhere else — a wiki page, a Swagger file, an engineer's memory — and an LLM has to be separately told to go read it, parse it, and hope it correctly infers how to call the endpoint. That's a lot of indirection sitting between an agent's intention and its ability to act.

MCP's core move is to eliminate that indirection: the tool's description lives *in* the interface itself, in a form built specifically to be digestible by a language model, not a human reading API docs in a browser. This sounds like a small change. In practice it is the difference between an agent guessing at how to use ten different bespoke APIs and an agent reading one standardized, self-describing interface for all of them.

This page covers what MCP actually standardizes, why documentation quality is not optional for it to work, and the surprising claim from the course that MCP's reach goes well past software into physical systems.

## Core intuition

MCP is a generalization of the REST API idea, purpose-built for consumption by an LLM rather than a human developer. Where a REST API separates "what the endpoint does" (the documentation) from "how you call it" (the schema), MCP folds both into a single, declarative interface an agent's LLM can read directly at decision time, with minimal ceremony required to turn a function into a tool an agent can discover and safely invoke.

## Why it matters

The practical cost of the old approach — REST plus separately-maintained docs — is that an LLM has to either be pre-trained on that specific API's documentation (impossible for internal or novel APIs) or have the docs stuffed into its context at query time, parsed on the fly, with all the ambiguity that entails. MCP tools instead carry their own documentation, typically as docstrings, directly in the interface the MCP server exposes — this is literally what the server hands to the agent's LLM so it can decide whether and how to use the tool. Good documentation stops being a nice-to-have for human maintainers and becomes the mechanism by which the agent decides what to do.

MCP's second underappreciated point is scope: the protocol was designed to cover more than software functions. An MCP "tool" can be a physical actuator — a camera, a robotic arm, a lathe. The course's engineering example is a lathe machine cutting a metal cylinder: an agent uses an MCP camera tool to observe the spinning block, measure its radius, and guide the cutting tool to the target dimension. The tool interface pattern — described capability, invoked action, observed result — is the same whether the "tool" mutates a database row or mutates a physical object.

## Instructor framing

Open with the REST-vs-MCP contrast before anything else, because most students already have a mental model of REST APIs and the fastest way to teach MCP is to show precisely what changes relative to that model: the documentation moves inside the interface, and the interface is written for a model to read, not a human. Once that lands, the physical-AI extension (cameras, lathes, robots) should be introduced as evidence that this isn't a software-specific trick — it's a general pattern for "how does a reasoning agent discover and safely use a capability," regardless of whether that capability lives in a database or a workshop.

## Worked example

Take a simple MCP camera tool: it captures an image and returns it. Its documentation, embedded as a docstring the MCP server exposes, might say: "Captures a still image from the connected camera. Returns a base64-encoded JPEG. No arguments required. Latency: under 200ms." An agent's LLM, given a task that requires visual observation, reads this description and can decide, on its own, that this tool is the right one to call — no external documentation lookup, no pre-training on this specific camera's API.

Now chain it with a second, more complex tool: an image-recognition tool built on a facial-recognition library and a vision-language model, documented as: "Given an image, returns a natural-language description of people present, including approximate count and, if recognizable, identity." An agent answering "how many people are in the living room?" can now compose these two tools — call the camera tool, feed its output into the recognition tool — purely by reading each tool's self-contained description, exactly the kind of composition MCP is designed to make trivial.

## Math explained step by step

Quantify the integration cost MCP removes, since "standardization" is a vague claim without a concrete cost comparison.

**Step 1 — cost of ad hoc integration.** Without a shared protocol, integrating $n$ tools into an agent requires the agent's developer to write $n$ separate pieces of glue code, each translating that tool's specific API shape into something the LLM can be prompted about — call this cost $g$ per tool, for a total integration cost of $ng$.

**Step 2 — cost under MCP.** Once a tool exposes an MCP-compliant interface (self-describing, standardized schema), integrating it into any MCP-aware agent costs a small, roughly fixed amount $\delta \ll g$ — mostly just pointing the agent at the tool's address, since the documentation and calling convention are already in the standardized shape the agent expects. Total integration cost across $n$ tools becomes $n\delta$.

**Step 3 — the crossover.** Since $\delta \ll g$, the savings $n(g - \delta)$ grow linearly with the number of tools — and grow faster still once you account for reuse: a tool built once, MCP-compliant, can be integrated into *every* future agent at cost $\delta$, not just the one it was built for, whereas an ad hoc integration typically has to be redone per consuming agent.

**Step 4 — the registry effect.** Add an MCP registry — a curated, vetted list of approved tools for a domain — and the discovery cost (finding which tool does what you need) also drops, because an agent (or its developer) searches one registry instead of asking around or trawling documentation across teams; this further compounds the $n\delta$ savings by reducing the constant hidden inside $\delta$ itself.

## Practical pattern

Building an MCP tool that agents will actually use reliably:

1. write documentation as if it's the only thing the agent will ever see about this tool — because it is; the docstring is the interface, not an afterthought;
2. make heavy or slow operations asynchronous, since MCP tools backed by real computation (especially model inference) can have significant latency, and blocking calls degrade the whole agent's responsiveness;
3. use streaming HTTP where results arrive incrementally, and build in retries — models and systems fail, and a tool that doesn't tolerate transient failures becomes a single point of unreliability for every agent that depends on it;
4. use current library versions (the course specifically flags FastMCP 2.0+ over outdated 1.0 tutorials) since MCP tooling is evolving quickly and older tutorials can teach patterns that no longer reflect best practice;
5. register production tools in a curated registry rather than leaving discovery to word-of-mouth, reducing the odds an agent picks an overlapping, poorly-maintained, or deprecated tool by mistake.

## Common traps

- treating documentation as optional or writing it for a human maintainer's benefit rather than as the actual decision-making input an agent's LLM will use — vague or incomplete docstrings directly cause an agent to misuse or ignore a tool;
- building heavy, GPU-bound tool logic as blocking synchronous calls, which quietly turns one slow tool into a bottleneck for every agent that calls it;
- assuming MCP is a software-only concept and missing that the same self-describing-interface pattern applies to physical actuators, sensors, and robotics — a narrower mental model than the protocol actually supports;
- following outdated tutorials built on early MCP tooling versions, missing best practices (async, streaming, retries, registries) that later versions and enterprise deployments have converged on.

## Takeaways

- MCP generalizes REST by making a tool's documentation part of its interface, in a form built for an LLM to read at decision time — removing the indirection of separately-maintained API docs.
- Documentation quality is not a maintenance nicety for MCP tools; it is the literal input an agent's LLM uses to decide whether and how to call the tool, so vague docstrings directly cause misuse.
- MCP's reach extends beyond software APIs to physical systems — cameras, robotic actuators, industrial equipment — because the underlying pattern (described capability, invoked action, observed result) is the same regardless of what the tool actually touches.
