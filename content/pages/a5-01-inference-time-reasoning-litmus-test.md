---
id: a5-01-inference-time-reasoning-litmus-test
title: "The Litmus Test: Agent or Tool?"
week: 5
topic: "Act I: Agent or Tool? The Litmus Test"
order: 1
summary: The only reliable way to decide whether a piece of functionality should be an Agent or a Tool is to ask whether it needs inference-time reasoning — everything else is a naming argument.
course: ai_agents
---

Every team that starts building agentic systems eventually has the same argument, usually around week two of a real project: is this thing we just wrote an agent, or is it a tool? Someone points out that the "summarize this text" function calls an LLM, so surely it's an agent. Someone else points out that "open this file" clearly isn't. The argument stalls because both sides are reasoning from surface features — does it call a model, does it sound smart — rather than from the one property that actually matters.

The mistake is treating "uses an LLM" as the dividing line. A huge amount of what gets called agentic behavior is really just a function that happens to have a language model inside it, producing the same kind of deterministic-enough output every time it's called with similar input. That's a tool wearing a costume. The reverse mistake also happens: teams write elaborate orchestration code for something that is, underneath, a simple rules engine with no autonomous reasoning in it at all, and call the orchestration an "agent framework."

There is a real test here, and it isn't about vibes. It's about whether a specific kind of decision has to be made *at the moment the function runs*, using information that didn't exist until that moment.

## Core intuition

The litmus test is inference-time reasoning: does the function need to reason about information that only became available at the moment of execution, in order to decide what to do?

If the answer is no — if the logic could, in principle, have been fully specified in advance, as a flowchart, a rules engine, or a fixed sequence of steps — then it is a tool, or a static workflow, no matter how sophisticated its internals look. If the answer is yes — if the function has to look at something novel and make a judgment call that wasn't fully determined beforehand — it is exercising agency, and the component built around that judgment call is an agent.

Capitalizing text or running named-entity recognition is a tool: the steps are deterministic and require no autonomous thought, even though NER might internally use a neural network. A researcher agent that has to look at a freshly returned list of search results and decide which five are "best" is doing inference-time reasoning, because that search list — and therefore the judgment about what's best within it — did not exist until the moment of execution.

## Why it matters

This distinction is not academic pedantry about vocabulary. It determines how you architect a system. Tools are meant to be small, reusable, stateless, and predictable — you write one once and call it from a hundred different places with confidence that it behaves the same way each time. Agents are meant to be autonomous reasoners, and you should expect their behavior to vary with context, because that variability is the entire point of having them.

If you misclassify an agent as a tool, you'll try to make its behavior deterministic and get frustrated when it isn't — you're fighting the nature of the thing. If you misclassify a tool as an agent, you'll over-engineer it with planning loops and memory it doesn't need, adding latency and failure surface to something that should have been a one-line function call. Getting the classification right up front is what keeps a multi-component agentic system modular instead of turning into an undifferentiated blob of LLM calls that nobody can reason about independently.

## Instructor framing

Teach the decision tree before teaching any framework. Students who learn LangGraph or CrewAI first tend to import the framework's vocabulary uncritically — "everything is an agent because the framework calls it that." Establishing the litmus test first gives them an independent yardstick they can apply to any framework's marketing claims, including this course's own examples. When you introduce the "agent as a reusable tool" pattern in the next page, students who have internalized this test will immediately see why that pattern isn't a contradiction — it's the test applied twice, once to the interface and once to the internals.

## Worked example

Consider building a function that decides whether to send an alert when a house's back door opens. A naive version is `if back_door_open: send_alert` — pure deterministic logic, unambiguously a tool (in fact, barely more than a rule).

Now consider a more sophisticated version: the household has a dog, Sophie, who gets anxious, and the owners don't want an alert every time the back door opens while the front gate is closed, because that's a known-safe pattern — dog on the porch, gate secured. But they do want an alert if the gate is *also* open, or if it's late at night, or if Sophie's collar sensor shows elevated activity. Encoding every combination of these conditions as nested if/else logic becomes brittle fast, and new edge cases keep surfacing that nobody anticipated when the rules were written.

The reasoning version takes the current sensor state — a combination of signals that is different every time, in ways the developer can't fully enumerate in advance — and asks a model to judge, in context, whether this specific combination warrants an alert. That judgment, made fresh against novel input each time, is inference-time reasoning. The function has crossed from tool territory into agent territory, and the cost is real: token spend and latency the pure `if/else` version never had. The trade is only worth it because the flexibility the fixed rules couldn't provide is worth more than the cost.

## Math explained step by step

The decision tree from the course formalizes into two sequential yes/no questions, and it's worth walking the branches explicitly because the third branch is the one people get wrong.

**Step 1 — does it need inference-time reasoning?** If no, stop: this is a tool, unambiguously, regardless of how the code is organized internally. The keyword extractor's basic frequency count needs no reasoning about anything not knowable in advance — it is a tool by definition.

**Step 2 — if yes, is it a reusable, stateless component serving general functionality?** This is where the surprising branch lives. If the answer to step 2 is *no* — the reasoning is specific to one particular workflow, not meant to be called from elsewhere — the component is an Agent: a dedicated, autonomous entity defined for this job.

**Step 3 — if the answer to step 2 is *yes*,** the component is still built as a Tool externally — because reusability and statelessness are exactly the properties a Tool interface is designed to expose to callers — even though internally it behaves exactly like an agent, exercising judgment on each call. Symbolically: let $R$ = "needs inference-time reasoning" and $S$ = "reusable and stateless." The classification function is

$$\text{class}(R, S) = \begin{cases} \text{Tool} & R = \text{false} \\ \text{Agent} & R = \text{true},\ S = \text{false} \\ \text{Tool (internally an Agent)} & R = \text{true},\ S = \text{true} \end{cases}$$

The third row is not a special case to memorize; it falls directly out of applying the same test to two different questions — "does this need reasoning?" and "should callers see it as a stable, swappable interface?" — and noticing that the two answers can be independent of each other.

## Practical pattern

When you're not sure how to classify a piece of functionality you're about to build:

1. write down, concretely, what information the function needs that could not have been known when the code was written — if the list is empty, it's a tool;
2. if the list is non-empty, ask whether other teams, other agents, or other parts of your own system would plausibly want to call this same reasoning behavior — if yes, expose it as a Tool interface even though it reasons internally, so callers get a stable, swappable contract;
3. if the reasoning is genuinely one-off and specific to a single workflow, build it as a dedicated Agent and don't force a generic Tool wrapper onto it prematurely;
4. document which branch you chose and why, next to the code — the classification tends to erode silently as requirements change, and the comment is what lets the next engineer catch the drift.

## Common traps

- assuming "calls an LLM" is the test, and therefore classifying every LLM-backed function as an agent, even when its output is effectively deterministic given the input;
- assuming "doesn't call an LLM" means "must be a tool," missing that a rules engine with enough branching can still be encoding pre-determined logic that belongs in a workflow, not an agent, regardless of complexity;
- forgetting the third branch — building a bespoke, non-reusable agent for functionality that other parts of the system will clearly need later, instead of dressing it as a reusable Tool from the start;
- treating the Agent/Tool line as permanent — a function that starts as a one-off agent often becomes a candidate for the Tool treatment once a second caller shows up, and the code should be refactored accordingly rather than left as an awkward exception.

## Takeaways

- The only reliable test for Agent vs. Tool is whether the function needs inference-time reasoning over information that didn't exist until the moment of execution — not whether it happens to call a model.
- A function needing reasoning is still built and exposed as a Tool if it's reusable and stateless; internally it acts as an agent, externally it behaves like a tool. This is a deliberate architectural choice, not a contradiction.
- Getting this classification right early keeps a multi-agent system modular; getting it wrong produces either over-engineered agents doing tool-sized jobs, or brittle rule stacks pretending to be tools when they actually need judgment.
