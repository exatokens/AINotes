---
id: a8-07-internet-of-agents-agency-protocol
title: "MCP, A2A, and the Missing DNS for Agents"
week: 8
topic: "Act III: Trust at the System Level"
order: 7
summary: MCP handles agent-to-tool, A2A handles agent-to-agent, and neither solves directory-based discovery at internet scale — the Linux Foundation's Agency project is an attempt to build exactly that missing layer.
course: ai_agents
---

By this point in the course, MCP and A2A have each been covered on their own terms — MCP as the way an agent discovers and safely calls a tool, A2A as the way agents talk to other agents across process and organizational boundaries. What hasn't been addressed directly is what happens when you need both, simultaneously, in a single coherent ecosystem, and what's still structurally missing even once you have both.

The AI Doctor scenario is the course's device for making this concrete: a single system that needs to fetch data via a tool, communicate with billing and pharmacy as fine-tuned specialist agents, and do all of this in a way that could plausibly interoperate with agents built by entirely different organizations, on entirely different frameworks. Laying out exactly where MCP ends and A2A begins — and where both end and something new is still needed — is what this page is for.

## Core intuition

**MCP**'s primary focus is agent-to-tool: a client-host-server architecture where a host connects to servers it already knows about, requesting well-defined, typically stateless function calls. **A2A**'s primary focus is agent-to-agent: a more direct client-server model, where an "Agent Card" published at a well-known URL lets one agent discover another it already has an address for, then engage in potentially rich, stateful interaction. Both protocols solve real, distinct problems — but both share the same discovery limitation from earlier in the course: an agent needs to already know where to look before either protocol's discovery mechanism can help it.

The **Agency** project (from the Linux Foundation, operationalizing the "Internet of Agents" concept coined by Cisco and MIT) targets exactly this gap with a third architectural layer: a directory-based discovery model, closer to DNS, where agents from different organizations register themselves in an Agent Directory and other agents query it — "find me all agents with billing capabilities" — rather than needing to already know a specific address to check.

## Why it matters

The distinguishing feature across all three is architecture, and the course lays it out as a direct comparison: MCP is client-host-server with host-initiated connections to known servers; A2A is direct client-server with peer-to-peer, Agent-Card-based discovery; Agency is layered and directory-based, explicitly designed for cross-organization discovery the other two don't attempt to solve. This isn't redundancy — it's each layer solving a different piece of a genuinely larger problem, the way DNS, TCP, and HTTP each solve a different layer of the problem "get information from one computer to another across the internet" without any one of them alone being sufficient.

Agency's proposed infrastructure goes further than just discovery: it specifies Secure Low-Latency Interactive Messaging (SLIM) as a communication layer built to handle richer payload types (video, images) more robustly than standard HTTP, and explicitly acknowledges that a distributed registry serving this role is bound by the CAP theorem — it must trade off consistency, availability, and partition tolerance, and cannot guarantee all three simultaneously under real network conditions. This is the same constraint flagged when discussing centralized discovery generally, now attached to a specific, named effort trying to actually build the thing.

## Instructor framing

Teach the AI Doctor scenario as a single running example that forces students to correctly place each interaction into the right protocol category — fetching patient data via an MCP tool call, sending billing information to a specialized Billing Agent via A2A, sending a prescription to a specialized Pharmacy Agent via A2A — before introducing Agency as "and now imagine this AI Doctor needs to interact with a Billing Agent at a completely different hospital system it's never talked to before." That specific extension is what makes the gap between A2A's peer-to-peer model and Agency's directory-based model concrete rather than abstract.

## Worked example

Walk the AI Doctor's full interaction chain. It uses an MCP tool to fetch raw patient data from an FHIR-compliant database — a stateless, well-defined function call, exactly MCP's intended use case. It sends billing information to a Billing Agent — not a simple tool, but a specialized, fine-tuned model that only understands billing, communicating via A2A because this is a stateful, judgment-requiring interaction (the Billing Agent needs to interpret and act on the specifics of this case, not just execute a fixed function). It sends a prescription to a Pharmacy Agent, fine-tuned only on drugs, again via A2A for the same reason.

Now extend the scenario the way Agency is meant to address: the AI Doctor operates at Hospital A, and the patient's insurance requires interaction with a Billing Agent operated by an entirely different organization, Hospital B's billing system, which the AI Doctor has never previously integrated with and has no existing address for. Neither MCP (agent-to-tool, assumes known servers) nor A2A in its current peer-to-peer form (assumes you already have the other agent's address to request its Agent Card) solves this directly. Agency's Agent Directory is specifically designed for this case: the AI Doctor's system queries the directory for "billing agents authorized for this insurance network," discovers Hospital B's Billing Agent it had no prior knowledge of, and proceeds — the DNS-like function neither MCP nor A2A alone provides.

## Math explained step by step

Formalize why a three-layer stack (MCP, A2A, Agency) is structurally necessary rather than redundant, by examining what each layer's absence would break.

**Step 1 — model the problem as three coupled but distinct sub-problems.** Let $T$ be "safely invoke a well-defined function with known capability boundaries," $C$ be "communicate richly and statefully with another autonomous reasoner you can already reach," and $D$ be "find a relevant, trustworthy counterpart you have no prior address for." These are genuinely different problems: solving $T$ doesn't help with $C$ (a tool call doesn't need or support rich negotiation), and solving $C$ doesn't help with $D$ (knowing how to talk to an agent once found doesn't tell you how to find one you didn't know existed).

**Step 2 — map each protocol to the sub-problem it solves.** MCP solves $T$. A2A (in its current peer-to-peer form) solves $C$, given that $D$ has already been solved by some other means (manual configuration, prior integration). Neither solves $D$ on its own — A2A's Agent Cards *describe* an agent once found, but the peer-to-peer model doesn't specify how to find an agent you have zero prior information about.

**Step 3 — show why $D$ doesn't reduce to $T$ or $C$.** $D$ requires a registry with some minimal guarantee of availability and (approximate) consistency across a distributed set of registering organizations — a genuinely different kind of infrastructure than either a tool-calling protocol or a peer-to-peer negotiation protocol provides, because it requires coordinating *state about who exists* across parties that don't otherwise need to trust each other before discovery even happens.

**Step 4 — the CAP-theorem cost of solving $D$ properly.** Any real implementation of $D$ — Agency's Agent Directory being the current attempt — inherits the CAP theorem's fundamental trade-off: under a network partition, the registry must sacrifice either full consistency (some queriers might see stale or incomplete listings) or full availability (queries might fail outright rather than return possibly-stale data). This is not an engineering oversight to be fixed with more effort; it's a fundamental limit on any distributed registry, which is exactly why Agency's design has to make an explicit choice about which of the three CAP properties to prioritize, rather than promising all three.

## Practical pattern

Architecting a multi-agent system that needs to interoperate across organizational boundaries:

1. classify every interaction your system needs as $T$ (a tool call to a known, well-defined function), $C$ (rich communication with a known agent), or $D$ (discovery of an unknown, potentially cross-organizational counterpart) — and route each to the protocol layer actually designed for it, rather than trying to force one protocol to handle all three;
2. use MCP for anything that's genuinely a stateless function call with a well-defined capability boundary, even if the underlying implementation is internally agentic (per Week 5's dressed-as-a-tool pattern);
3. use A2A (or a comparable agent-to-agent protocol) for stateful, judgment-requiring interactions with agents you already know how to reach;
4. for genuinely open-ended, cross-organizational discovery needs, recognize that this remains the least mature layer of the stack — evaluate emerging directory-based efforts like Agency, understand their explicit CAP-theorem trade-offs, and don't assume "discovery" is a solved problem just because MCP and A2A both handle their respective adjacent pieces well;
5. design your own agent's registration and capability description to be reusable across whichever discovery mechanism eventually matures, rather than betting your entire integration surface on one specific, still-evolving standard.

## Common traps

- treating MCP and A2A as competing, redundant standards rather than complementary layers solving genuinely different problems ($T$ versus $C$), leading to awkward attempts to force tool-calling patterns into agent-to-agent interactions or vice versa;
- assuming A2A's peer-to-peer Agent Cards solve cross-organizational discovery, when they only solve communication with agents you already have an address for — the actual discovery gap ($D$) remains unaddressed by A2A alone;
- expecting a mature, production-ready directory-based discovery layer to already exist, when the course is explicit that Agency and comparable efforts are still early and actively grappling with fundamental distributed-systems constraints like the CAP theorem;
- building bespoke, one-off cross-organizational integrations in the absence of a mature discovery layer, without recognizing this is a stopgap that won't generalize the way a proper directory-based system eventually would.

## Takeaways

- MCP (agent-to-tool) and A2A (agent-to-agent) solve genuinely different problems and are complementary rather than competing — but both assume you already know how to reach the counterpart you're calling, whether it's a tool server or another agent.
- The Linux Foundation's Agency project targets the remaining gap: directory-based, DNS-like discovery for agents across organizational boundaries that neither MCP nor A2A's peer-to-peer model addresses.
- Any real directory-based discovery system inherits the CAP theorem's fundamental trade-off between consistency and availability under network partitions — this is a genuine distributed-systems limit, not a solvable engineering oversight, which is exactly why this layer of the stack remains the least mature even as MCP and A2A are already working in production.
