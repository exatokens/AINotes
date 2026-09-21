---
id: a5-06-three-architectures-direct-gateway-ray
title: "Three Levels of MCP Maturity: Direct, Gateway, Ray"
week: 5
topic: "Act III: From Prototype to Production — MCP Architecture"
order: 6
summary: MCP tool deployment matures through three stages — direct, gateway, and Ray-backed — mirroring the historical evolution of web servers, because AI workloads reintroduce exactly the isolation and scaling problems that mature server architecture already solved once.
course: ai_agents
---

Every MCP tutorial on the internet teaches the same first architecture: annotate a function with `@mcp.tool`, spin up a FastMCP server, done. It works, it's genuinely easy, and it is completely unsuited to running anything that matters in production. This isn't a criticism of the tutorials — it's the right place to start learning — but treating that starting point as a deployment architecture is a mistake that surfaces the moment real traffic, or a single misbehaving tool, hits the system.

What's useful about this material is that the failure mode isn't new or AI-specific. It's the same failure mode web server architecture solved decades ago, for the same underlying reason: putting untrusted or unreliable units of work directly in a shared process is fragile, and the fix — isolate execution, delegate to a managed compute layer — is a rediscovery of lessons the web already learned the hard way. What *is* AI-specific is the second half of the story: the constraint that makes the modern fix different from the old fix is the GPU, and its economics are inverted from everything traditional server engineering assumes.

## Core intuition

MCP tool architecture matures through three stages of increasing production-readiness: Direct (tools run in the server's own process), Gateway (the server delegates heavy work to a separate compute layer, most likely Ray), and Ray-backed production (the delegation model fully realized, with the MCP server reduced to a thin, stateless router). Each stage exists because the previous one has a specific, predictable failure mode under real load.

## Why it matters

In the **Direct** architecture, an `@mcp.tool`-annotated function runs inside the MCP server's own process. This is simple and has a low learning curve — genuinely the right choice for demos and early prototypes — but it has three compounding weaknesses: it's a single point of failure (one tool crashing takes the whole server down, the "apple cart" problem, since all tools share the same process space), it can't scale horizontally (bound to one process), and it can't manage GPU resources properly (no batching, no fractional allocation, prone to out-of-memory errors under concurrent load).

The **Gateway** architecture fixes the isolation and scaling problems by turning the FastMCP server into a thin router: incoming requests are logged and delegated to a separate, reliable compute cluster — the course points to Ray as the emerging standard for this layer — rather than executed in the server's own process. A failure in one tool's execution, now isolated in the Ray cluster, can no longer bring down the gateway or any other tool.

The **Ray-backed** stage completes this: tools are hosted as Ray remote functions or actors, automatically load-balanced and scaled across a cluster, with fine-grained GPU control (including fractional GPU allocation and automatic mini-batching) that a plain container-based scaling approach can't provide, because GPUs — unlike CPUs — don't parallelize cheaply across arbitrary numbers of processes without careful scheduling.

## Instructor framing

Present the historical parallel explicitly and early — process-per-request (early Apache/CGI) → threads-in-a-process (Tomcat/JBoss) → mixed models with speculative execution — before naming Direct/Gateway/Ray, so students recognize this as a rediscovery of established engineering wisdom rather than a novel AI problem needing novel first-principles thinking. Then pivot hard to what's genuinely new: traditional server engineering optimizes for staying comfortably under 50% utilization because hardware is cheap and downtime is expensive; AI infrastructure inverts this because GPUs are the scarce, expensive resource, and the goal becomes 100% GPU utilization even at higher operational risk. Students who don't see this inversion explicitly will keep importing "run cool, stay under capacity" instincts into a domain where the economics say the opposite.

## Worked example

A team ships their first MCP tool using the Direct architecture: a facial-recognition tool that loads a vision-language model into the same process as their `@mcp.tool` decorated function. It works fine in testing. In production, three things go wrong in sequence: first, a malformed image input causes an unhandled exception inside the recognition code, which crashes the entire MCP server process — taking down every *other* tool hosted in that same process, including an unrelated document-summary tool that had nothing to do with the failure. Second, under concurrent load from multiple agents, the single process can't parallelize GPU inference requests, so requests queue up and latency balloons. Third, without batching, each request creates its own model forward pass, wasting the GPU's parallel processing capability that batching would otherwise exploit.

Moving to the Gateway architecture immediately fixes problem one: the recognition logic now runs in an isolated Ray worker, so a crash there no longer takes the MCP process (now a pure router) down with it. Moving further to a fully Ray-backed deployment fixes problems two and three: Ray Inference queues and mini-batches concurrent requests automatically, and its fractional-GPU control lets the team run this tool alongside others on the same physical GPU without contention, driving utilization toward the 100% target that justifies the GPU's cost in the first place.

## Math explained step by step

Formalize why GPU-aware scheduling changes the utilization target, since "aim for 100% utilization" sounds reckless until you see the cost asymmetry driving it.

**Step 1 — traditional server sizing.** Classic capacity planning keeps utilization $u$ below a safety threshold, commonly around 50-60%, because the cost of an outage from an unexpected spike (customer-facing failure, SLA breach) vastly exceeds the cost of idle CPU capacity — CPUs and commodity servers are cheap, so provisioning headroom is the economically rational choice: minimize $P(\text{outage})$ even at the cost of low average utilization.

**Step 2 — invert the cost terms for GPUs.** Let $C_{\text{gpu}}$ be the amortized cost of a GPU (high, and often the dominant infrastructure line item) and $C_{\text{idle}}$ be the cost of that GPU sitting unused for a unit of time (still $C_{\text{gpu}}$'s full carrying cost, since idle GPU time is not refunded). Because $C_{\text{gpu}} \gg$ the equivalent CPU cost, the economically rational target shifts toward maximizing utilization $u \to 1$ rather than minimizing outage risk at low $u$ — the loss from wasted GPU capacity now dominates the loss from occasional contention, flipping the sign of the optimization compared to step 1.

**Step 3 — mini-batching as the mechanism.** A GPU's throughput for many small requests processed one at a time is far below its throughput for the same requests processed in a batch, because the hardware's parallel lanes go underused per single-item forward pass. If batch size $B$ requests share one forward pass at cost roughly $k \cdot B^{p}$ for $p < 1$ (sub-linear scaling due to shared overhead), then per-request cost $k \cdot B^{p-1}$ strictly decreases as $B$ grows — this is the concrete mechanism by which Ray Inference's automatic batching pushes utilization up without a proportional cost increase.

**Step 4 — fractional allocation closes the gap further.** If a given tool's model only needs, say, a fifth of a GPU's compute per request, running it on a dedicated full GPU wastes the remaining four-fifths; fractional GPU allocation lets multiple such tools time-share one physical GPU, pushing aggregate utilization across the fleet toward the target established in step 2.

## Practical pattern

Choosing and building the right architecture stage for a given MCP deployment:

1. use the Direct architecture only for demos, prototypes, and tools with genuinely negligible compute needs (a "hello world" tool, a pure-CPU utility) — never for anything GPU-bound or user-facing at scale;
2. move to the Gateway pattern as soon as a tool involves real computation or model inference — the isolation benefit alone (no single tool crash takes down the whole server) is worth the added architectural complexity;
3. host GPU-bound tools in Ray from day one of any project intended to reach production, rather than writing quick prototype code and planning to "harden it later" — the course is explicit that prototypes reliably become production code before anyone gets time to redo them properly;
4. use Ray Inference's fractional-GPU and mini-batching controls deliberately, sized to the actual compute footprint of each tool's model, rather than defaulting every tool to a dedicated full GPU;
5. keep the MCP server itself stateless and dumb in the Gateway/Ray stages — its only job is routing and logging, so that scaling the router (a cheap, commodity operation) never gets entangled with scaling the GPU-bound compute layer (an expensive, carefully-managed one).

## Common traps

- keeping the Direct architecture past the prototype stage because it "still works," until a single misbehaving tool takes down every other tool sharing its process;
- treating GPU capacity planning like CPU capacity planning, provisioning for low utilization and headroom, and consequently paying for GPU capacity that mostly sits idle — the opposite of what the cost asymmetry recommends;
- calling requests to a model one at a time without batching, leaving most of a GPU's parallel throughput unused even when overall demand would justify much higher effective capacity;
- writing "temporary" prototype code with the intention of properly architecting it before production, when in practice time pressure means the prototype ships as-is — the fix is architecting for isolation and scale from the very first version, not deferring it.

## Takeaways

- MCP tool deployment has three maturity stages — Direct, Gateway, Ray-backed — and each fixes a specific, predictable failure of the one before it: process isolation, then horizontal scale, then GPU-aware scheduling.
- This progression mirrors the historical evolution of web servers (process-per-request → threaded application servers → mixed models), because the underlying isolation and scaling problems are the same; what's new is the GPU-driven inversion of the utilization target from "stay under capacity" to "maximize utilization."
- Build GPU-bound MCP tools on Ray from the start of any project headed toward production — prototypes reliably become production code, so the isolation and batching benefits need to be present from day one, not retrofitted later.
