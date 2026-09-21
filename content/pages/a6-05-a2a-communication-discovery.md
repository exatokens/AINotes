---
id: a6-05-a2a-communication-discovery
title: "A2A: Discovery Is the Whole Problem"
week: 6
topic: "Act II: When Agents Must Talk to Other Agents"
order: 5
summary: Agent-to-Agent communication has to solve the same discovery problem the internet solved with DNS, and today's peer-to-peer Agent Cards are a known-good-enough solution, not the long-term one.
course: ai_agents
---

Once agents need to talk across process and organizational boundaries, the interesting engineering problem stops being "how do we format the message" and becomes "how does an agent even know another agent exists, and where to find it." This is not a new problem in computing — it's the same problem the early internet had before DNS existed, the same problem CORBA and DCOM fought over in the 1990s — but it's being solved again, from scratch, for a new class of participant: autonomous reasoning agents instead of static services.

The current landscape is genuinely unsettled. Google's A2A, IBM's ACP, MIT's NANDA, and Cisco's Internet of Agents vision are all live proposals, and there is no single winner yet — the course frames this explicitly as a "protocol war," with the useful historical prediction that in past protocol wars, the simpler protocol tended to win, not the most feature-complete one. A2A's recent transfer to the Linux Foundation is one datapoint suggesting where momentum is heading, but it's a datapoint, not a conclusion.

## Core intuition

Discovery in multi-agent systems splits into two models. **Peer-to-peer discovery** — the current A2A approach — has agents exchange Agent Cards: structured descriptions (in something like YAML) of an agent's capabilities, policies, and location, obtained directly from the agent you already know how to reach. This works well for known peers but doesn't scale to finding an agent you've never heard of before, because you need its address before you can ask it for its card in the first place — a chicken-and-egg problem baked into the peer-to-peer model.

**Centralized discovery** is the longer-term vision: a broker or DNS-like registry where agents register their capabilities, and other agents query the registry ("find me all agents with 'health service' capabilities") rather than needing to already know who to ask. This is what's required for genuine internet-scale, "internet of agents" interaction, and it remains largely futuristic — not because the idea is hard to state, but because building trustworthy, decentralized registries at that scale is a genuinely unsolved distributed-systems problem, with technologies like blockchain floated as candidate approaches for maintaining such registries securely.

## Why it matters

The peer-to-peer/centralized split isn't an implementation detail — it determines what kinds of multi-agent systems are even possible today versus what remains aspirational. A closed ecosystem where you already know every agent you'll ever need to talk to (a company's internal multi-agent deployment, say) can work fine with peer-to-peer Agent Cards indefinitely. A truly open "internet of agents," where your agent might need to discover and interact with an agent built by an unrelated organization it has never heard of, structurally requires the centralized/brokered model — and that model doesn't yet exist in a mature, widely-adopted form.

This is also where the historical CORBA/DCOM/REST parallel earns its place: those distributed-object protocol wars were eventually won by REST, not because REST was the most powerful option on the table, but because it was simple enough that it actually got adopted everywhere. The course's prediction — that A2A-style protocols will likely converge the same way, toward whichever proposal is "good enough" and simple rather than maximally complete — is a genuinely useful piece of engineering judgment for anyone deciding how much to invest in any one specific standard today.

## Instructor framing

Use the DNS analogy as the single organizing frame for this entire page: peer-to-peer Agent Cards are "you already have the phone number," and centralized discovery is "you look the name up in a directory." Every other detail — Agent Cards' YAML structure, the specific competing standards, the CAP-theorem constraints on any distributed registry — hangs off that one analogy. Students who can explain why DNS was necessary for the human internet will immediately see why an equivalent is necessary for an internet of agents, and why peer-to-peer alone was never going to be the end state.

## Worked example

A hospital deploys an internal "AI Doctor" agent that needs to interact with a Billing Agent and a Pharmacy Agent — both known, both internal to the same organization, both reachable at fixed, well-known addresses. Peer-to-peer discovery via Agent Cards works perfectly here: the AI Doctor agent already knows where the Billing Agent lives, requests its Agent Card describing its capabilities and policies, and proceeds. No registry needed, because the set of relevant peers is small, fixed, and known in advance.

Now extend the scenario: the hospital wants its Pharmacy Agent to automatically check drug availability and pricing across a network of independent, unaffiliated pharmacy chains it has never directly integrated with before — a genuinely open discovery problem. Peer-to-peer breaks down immediately, because the Pharmacy Agent doesn't know these chains' addresses to request their Agent Cards in the first place. This is exactly the scenario the centralized/DNS-like model is meant for: a registry the Pharmacy Agent can query — "find me pharmacy-chain agents servicing this ZIP code" — without needing prior knowledge of who exists to ask.

## Math explained step by step

Formalize the cost difference between peer-to-peer and centralized discovery as the agent population grows, since "doesn't scale" needs a mechanism.

**Step 1 — peer-to-peer discovery cost.** If an agent needs to discover $k$ new peers it doesn't already know, and there's no registry, discovery requires some external, out-of-band mechanism (documentation, manual configuration, word of mouth) for each new peer — a cost that doesn't shrink as the total population of agents $N$ grows, because peer-to-peer discovery has no mechanism for *searching* an unknown population; it only handles peers you already have an address for.

**Step 2 — centralized discovery cost.** With a registry holding capability descriptions for all $N$ agents, discovering $k$ new peers with a specific capability costs one query against the registry, roughly $O(\log N)$ or better with reasonable indexing, regardless of how large $N$ is — the cost of *finding* peers is decoupled from the cost of having known them in advance.

**Step 3 — the crossover as $N$ grows.** As the total agent population $N$ grows (moving from "one hospital's internal agents" toward "the internet of agents" scale), peer-to-peer's reliance on prior-knowledge-based discovery becomes an increasingly severe bottleneck, while centralized discovery's query cost grows only logarithmically — this is the same shape of argument that made DNS necessary once the internet grew past the point where a shared hosts file (a peer-to-peer-style, hand-maintained address list) could keep up.

**Step 4 — the CAP-theorem constraint on the fix.** A distributed registry serving this role is still bound by the CAP theorem: it must trade off consistency, availability, and partition tolerance, since it cannot guarantee all three simultaneously under network partitions. This is precisely why a mature "internet of agents" registry is a harder distributed-systems problem than it might first appear — it's not just "build a lookup table," it's "build a lookup table that stays correct and available under exactly the failure conditions a global, decentralized deployment will actually encounter."

## Practical pattern

Choosing a discovery strategy for a real multi-agent deployment:

1. if your agent population is closed and known in advance (internal to one organization, or a small set of pre-established partners), peer-to-peer Agent Cards are sufficient and simpler to deploy than standing up a registry;
2. if your system needs to discover agents outside a known, closed set — genuinely open-ended partner discovery — recognize this requires a centralized or federated registry, and budget for the fact that mature, trustworthy implementations of this are still an emerging, not a solved, part of the ecosystem;
3. when evaluating which A2A-adjacent standard to adopt (A2A, ACP, NANDA, or others), weight simplicity and current momentum (the Linux Foundation transfer is a signal, not a guarantee) alongside feature completeness — the CORBA/DCOM/REST history suggests the simpler option tends to win adoption races, even against more powerful competitors;
4. design your own agent's capability description (its Agent Card equivalent) to be reusable across multiple discovery mechanisms where possible, so a future move from peer-to-peer to centralized discovery, or a shift between competing standards, doesn't require rebuilding the capability description itself from scratch.

## Common traps

- assuming peer-to-peer Agent Cards will "scale up eventually" into open, internet-wide discovery without architectural change — the chicken-and-egg problem (you need an address to ask for a card) doesn't get smaller as the population grows; it gets structurally worse;
- betting heavily on a single named standard (A2A, ACP, or another) as if the protocol war is already settled, when the course is explicit that this remains an open competition with real uncertainty about the eventual winner;
- treating "build a centralized agent registry" as a straightforward engineering task, underestimating that it inherits the full weight of distributed-systems constraints like the CAP theorem, not just a simple lookup-table implementation;
- building bespoke, one-off discovery mechanisms per partner integration instead of recognizing the pattern early and investing in something that generalizes as the number of external agents you need to reach grows.

## Takeaways

- Multi-agent discovery has two models: peer-to-peer (Agent Cards, works for known peers, doesn't solve "find an agent I've never heard of") and centralized/brokered (a DNS-like registry, required for genuinely open, internet-scale discovery, still largely futuristic in mature form).
- The current A2A/ACP/NANDA landscape is an unsettled protocol war, and history (CORBA vs. DCOM vs. REST) suggests the eventual winner is more likely to be whichever option is simple enough to actually get adopted everywhere, not necessarily the most feature-complete.
- A centralized agent registry is not merely a lookup table — it inherits real distributed-systems constraints (the CAP theorem) that make it a genuinely hard problem, which is exactly why it remains the less mature half of the discovery story even as peer-to-peer discovery is already working in production today.
