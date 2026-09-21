---
id: a1-05-agents-vs-programs-workflows
title: "Agents, Programs, and the Trap of Programming in English"
week: 1
topic: "Act II: What Is An Agent"
order: 5
summary: Programs and workflows execute explicit, hardwired instructions; agents are given a goal and reason autonomously about how to reach it — and micromanaging an agent with step-by-step instructions is a contradiction in terms.
course: ai_agents
---

There is a specific, avoidable mistake that this course calls "programming in English," and it deserves its own page because it is probably the single most common way teams build something that looks like an agent and behaves like a particularly unreliable script. The mistake is simple to describe: you take an LLM, and instead of giving it a goal and letting it reason about how to reach that goal, you give it an exhaustively detailed, step-by-step natural-language procedure — effectively writing a computer program, except in English instead of Python.

This combines the worst of both worlds. You don't get the determinism and reliability of actual code, because natural language instructions executed by a stochastic model still vary. And you don't get the benefit of agentic autonomy either, because you've pre-decided every step, leaving the model no room to adapt when reality doesn't match your assumed procedure. It is possible to build a system that is simultaneously less reliable than code and less capable than an agent, and "programming in English" is exactly how you get there.

## Core intuition

A program or workflow is a static, hardwired sequence of instructions: given input X, always do steps 1 through N in that exact order. An agent is given a goal and a role, and is trusted to determine its own sequence of steps, adapting that sequence to whatever it actually observes. The dividing line is not "does it use an LLM" — it's whether the system has genuine latitude to decide *how* to proceed, or whether that decision has already been made by the developer and merely phrased in prose.

## Why it matters

An "agent" that has been given no discretion is a contradiction in terms — the word itself implies agency, the capacity for independent decisions. Many systems marketed as having "thousands of agents" are, on inspection, thousands of prompts executing fixed procedures — a prompt library dressed in agentic language. This matters because it sets the wrong expectations for what the system can handle: a hardwired workflow, even a very long and detailed one, cannot generalize to a scenario its author didn't anticipate, while a genuine agent can — provided its reasoning is sound and its tools are adequate.

## Instructor framing

Give students a two-question litmus test they can apply to any system, including their own homework projects: (1) does the problem require autonomous reasoning in a fluid, not-fully-anticipated environment? (2) is the problem complex enough to require decomposition into subtasks the developer didn't fully spell out in advance? If both answers are genuinely "no," a deterministic workflow is not a lesser choice — it is the *correct* choice, and building an agent instead is over-engineering, "reminiscent of the historical misuse of design patterns where even trivial programs like FizzBuzz were overloaded with unnecessary complexity."

## Worked example

The recap's genie story makes the contrast concrete. Aladdin does not tell the genie "first acquire 10,000 bricks, then survey the land, then hire laborers in this order." He states a goal: "build me a castle." The genie reasons, plans, and acts autonomously to reach that outcome — sourcing materials however it judges best, in whatever order the situation calls for. Contrast this with a travel-booking chatbot whose designer writes: "First ask for destination. Then ask for dates. Then ask for budget. Then call the flight API. Then call the hotel API. If flight API fails, say 'sorry, try again later.'" This second system might use an LLM to parse the user's replies at each fixed step, but it is not reasoning about the plan — the plan was fully decided by its author. It cannot adapt if a user says "actually, I don't care about dates, just find me the cheapest week this month" unless that exact deviation was separately hardwired in. A genuine travel *agent*, given the goal "book me a good trip to Hawaii," would reason about what "good" requires (weather, cost, availability), decide which of those to check first based on what it learns, and adapt its plan as it observes results — exactly the reasoning cycle a fixed workflow cannot perform.

## Math explained step by step

The trade-off between workflows and agents can be quantified along two axes: reliability and coverage, and it clarifies exactly when each is the right engineering choice.

**Step 1 — define coverage as the fraction of real-world scenarios handled correctly.** A hardwired workflow with $k$ explicitly anticipated branches handles some coverage $\text{Cov}_{\text{workflow}}(k)$ that grows only as fast as the developer's enumeration effort — it is bounded above by however many scenarios were actually anticipated and coded, and it is exactly $0\%$ on anything outside that enumerated set, no matter how sophisticated the prompt wording inside each branch is.

**Step 2 — define an agent's coverage as bounded by its reasoning quality, not enumeration effort.** An agent's coverage is $\text{Cov}_{\text{agent}} \approx q_{\text{reason}} \cdot \text{Cov}_{\text{tools}}$, where $q_{\text{reason}}$ is the probability its reasoning correctly handles a novel situation and $\text{Cov}_{\text{tools}}$ is the fraction of the goal space its available tools can actually reach — critically, this does not require the developer to have enumerated the scenario in advance.

**Step 3 — see the crossover.** For a narrow, fully-enumerable task (a fixed data-entry form, say), $k$ can realistically approach $100\%$ of real scenarios with modest effort, and $\text{Cov}_{\text{workflow}}(k)$ will beat $\text{Cov}_{\text{agent}}$ while also being cheaper (no LLM reasoning call needed at all) and perfectly deterministic. For a genuinely open-ended task (planning a trip, writing a performance review), the number of realistic scenarios is combinatorially large, $k$ can never practically approach full coverage, and $\text{Cov}_{\text{agent}}$ — even with an imperfect $q_{\text{reason}}$ — starts winning once $q_{\text{reason}} \cdot \text{Cov}_{\text{tools}}$ exceeds the workflow's achievable $\text{Cov}_{\text{workflow}}(k)$ for realistic $k$.

**Step 4 — apply this to "programming in English."** Writing an exhaustive natural-language procedure is an attempt to raise $k$ (enumerate more branches) while paying an LLM-call cost at every step — it inherits the workflow's coverage ceiling *and* the agent's cost and latency profile, which is exactly the worst-of-both-worlds outcome the course warns about.

## Practical pattern

1. Apply the two-question litmus test (fluid environment? needs decomposition?) before deciding whether a task needs an agent at all.
2. When a task fails the litmus test, build a deterministic workflow — it will be cheaper, faster, and more reliable, and using an LLM inside a fixed step (e.g., parsing free-text input into a structured field) does not make the overall system an agent.
3. When a task passes the litmus test, specify a goal and a role, not a numbered procedure — give the agent the "what," and reserve explicit steps only for genuine hard constraints (compliance rules, safety limits) rather than for the entire plan.
4. Periodically audit "agent" systems already in production for hidden over-specification — a system nominally built as an agent but driven by an exhaustive step-by-step prompt is a workflow wearing an agent's clothing, and should be evaluated (and priced) as one.

## Common traps

- Calling a large library of fixed prompts an "agentic system" because each prompt happens to call an LLM — the defining feature of agency is discretion, not LLM usage.
- "Programming in English": writing exhaustive, step-by-step natural-language instructions that strip away an agent's ability to adapt while still paying the cost and inconsistency of an LLM call at every step.
- Over-engineering a fully enumerable, low-complexity task into an agentic system because agentic frameworks are fashionable, when a simple deterministic workflow would be more reliable and cheaper.
- Assuming that adding more detail to a fixed procedure improves reliability — past a point, added detail only raises $k$ marginally while the task's true scenario space remains combinatorially larger.

## Takeaways

- Programs and workflows execute explicit, pre-decided sequences; agents are given goals and reason autonomously about the sequence.
- "Programming in English" — an exhaustive natural-language procedure fed to an LLM — combines a workflow's coverage ceiling with an agent's cost and inconsistency, the worst of both worlds.
- A two-question litmus test (does it need fluid reasoning? does it need decomposition?) tells you honestly whether a task calls for an agent or a workflow — and "no" is often the right, and cheaper, answer.
- True agency means specifying the goal, not the procedure — the moment you find yourself numbering steps in a system prompt, ask whether you're actually building a workflow.
