---
id: a6-09-response-grounding-storm-vs-langgraph
title: "Response Grounding, and What Storm Knows That LangGraph Doesn't"
week: 6
topic: "Act III: Agentic RAG — When Retrieval Needs a Planner"
order: 9
summary: A response-side guardrail agent must check grounding, relevance, completeness, and toxicity before an answer reaches a user — and Stanford's Storm system shows what a genuinely dynamic, plan-from-scratch agentic system looks like, in contrast to LangGraph's a priori graphs.
course: ai_agents
---

Everything upstream in an agentic RAG pipeline — query rationalization, semantic caching, exploratory search — is in service of getting good evidence in front of a language model. None of it guarantees the model actually uses that evidence faithfully once it's there. A model can be handed exactly the right retrieved passages and still produce an answer that drifts from them, misses part of the question, or says something harmful in a domain sensitive enough that "plausible-sounding" isn't good enough. That's what the response-side guardrail agent exists to catch, and it closes the loop this whole week has been building toward: a system that plans, retrieves, generates, and then checks its own output before it goes anywhere.

The second half of this page pulls back to a bigger question the whole week has been circling: what does a *fully* dynamic agentic system look like, one that doesn't just check its own output but plans its own structure from nothing? Stanford's Storm system is the course's answer, and it's worth taking seriously as a genuine contrast case to LangGraph, not just a research curiosity.

## Core intuition

Before a generated response reaches a user, a response-side guardrail agent should check: **grounding/hallucination** — does the answer accurately reflect the retrieved sources, or does it introduce claims the evidence doesn't support; **relevance** — does the answer actually address what was asked, checkable via embedding similarity between the query and the response; **completeness** — does the answer cover every part of a multi-part question, or silently drop pieces; and **toxicity/risk/bias** — does the answer contain harmful, inappropriate, or dangerous content, illustrated by the course's own cautionary example of a chatbot giving genuinely dangerous dating advice. If a response fails any of these checks, the agent can block it, trigger regeneration, or send the query back through another round of exploratory search to find better evidence — the same cyclical, self-correcting shape that characterizes advanced agentic RAG throughout this week.

Storm, by contrast, is introduced as a demonstration of what LangGraph-style frameworks structurally cannot do: rather than executing a pre-defined graph, Storm dynamically conjures both the plan *and* the specific agents needed to execute it, from scratch, based on the input topic — a fundamentally different kind of flexibility than choosing among pre-wired branches.

## Why it matters

The response-grounding checks matter because they're the last line of defense in the entire pipeline, and they catch failure modes none of the upstream mechanisms address. Good retrieval and good context engineering reduce the *chance* of a bad answer, but they don't guarantee the model's generation step stays faithful to what it was given — grounding checks are the only mechanism in the whole stack that verifies faithfulness directly, after the fact, rather than trying to prevent unfaithfulness upstream. This is also why the check needs to be cyclical rather than a simple pass/fail gate: a failed grounding check doesn't mean the system should just apologize and stop — sending it back through exploratory search for better evidence, or triggering regeneration with the same evidence, are both legitimate recovery paths depending on whether the problem was insufficient evidence or the model's handling of adequate evidence.

Storm matters because it's concrete proof that "dynamic planning" isn't just a theoretical alternative to LangGraph's a priori graphs — it's been built and demonstrated, successfully generating a detailed, well-structured Wikipedia-style article on "Automation of Clinical Workflows in Medical Physics," complete with references and technical discussion, by dynamically spawning topic-specific agents (a Clinical Decision Support Analyst, a Medical Physics Editor, a Health Informatics Specialist Editor, a Basic Fact Writer) that didn't exist as pre-defined roles before the topic was given, and having them collaboratively ask clarifying questions, research their specific angles, and synthesize a result — all without a human pre-wiring which agents would be needed or how they'd interact.

## Instructor framing

Close the week on this contrast deliberately: LangGraph is the right tool when the graph is 80% known in advance (this week's Act I established why), and Storm is what genuinely open-ended, exploratory-planning problems require instead. Neither is "better" in the abstract — they're suited to different problem shapes, and a mature engineer should be able to look at a new problem and correctly judge which shape it has, rather than defaulting to whichever framework they already know. The response-grounding checklist, meanwhile, should be taught as non-negotiable regardless of which planning architecture sits upstream of it — a Storm-style dynamically-planned system needs response grounding just as much as a LangGraph-style fixed-workflow system does, because grounding failures happen at generation time, independent of how the plan that led there was constructed.

## Worked example

A response-grounding agent receives a generated answer to "What are the side effects of Drug X, and is it safe during pregnancy?" — a two-part question. The generated response thoroughly covers side effects but never addresses the pregnancy-safety question at all. The completeness check catches this specifically: embedding similarity between the full question and the response might still look reasonably high (side effects *are* relevant to the question), but a completeness check comparing the response against each identified sub-question flags the missing half. The agent triggers another round of exploratory search specifically targeted at the missing sub-question, rather than accepting a half-answered response as good enough because it scored well on relevance alone.

Separately, consider Storm tackling a genuinely novel research-synthesis topic with no natural single-workflow shape — "assess the current landscape of AI regulation across three legal jurisdictions." A LangGraph-style system would need someone to pre-design a graph anticipating which sub-topics matter, which is exactly the kind of a priori structure this topic resists (the relevant sub-topics only become clear once initial research surfaces which jurisdictions have genuinely comparable frameworks and which don't). Storm's dynamic agent-spawning approach — creating jurisdiction-specific analyst agents, an editor agent to reconcile conflicting findings, and so on, all decided at runtime based on what the topic actually contains — handles this shape of problem in a way a fixed graph structurally cannot.

## Math explained step by step

Formalize the relevance-check mechanism (embedding similarity) since it's the one response-grounding check with a clean, quantifiable definition worth deriving.

**Step 1 — represent query and response as vectors.** Let $\vec{q}$ be the embedding of the original query and $\vec{a}$ be the embedding of the generated answer, both produced by the same embedding model so they live in a comparable vector space.

**Step 2 — compute cosine similarity as the relevance signal.**

$$\text{relevance}(\vec{q}, \vec{a}) = \frac{\vec{q} \cdot \vec{a}}{\|\vec{q}\|\,\|\vec{a}\|}$$

A high cosine similarity indicates the answer's semantic content is well-aligned with the query's; a low similarity suggests the answer has drifted onto a different topic than what was asked, even if it's coherent and well-formed prose on its own terms.

**Step 3 — extend to completeness for multi-part questions.** Decompose the original query into its constituent sub-questions $q_1, \ldots, q_k$ (the same factoid-style decomposition idea used for grounding checks elsewhere in this material), embed each separately, and compute $\text{relevance}(\vec{q_i}, \vec{a})$ for each. A low score on any individual $\vec{q_i}$ — even with a high aggregate score against the full combined question — flags that specific sub-question as inadequately addressed, which is exactly the mechanism that catches the drug-safety example's missing pregnancy-safety half above.

**Step 4 — the threshold decision as a policy choice, not a fixed constant.** Setting the similarity threshold below which a response is flagged for regeneration is itself a trade-off along the same suspicion-vs-disclosure axis as any exit-gate design: a stricter threshold catches more genuine incompleteness at the cost of more false-positive regenerations (increasing latency and cost); a looser threshold lets more genuinely incomplete responses through. The right value depends on the cost asymmetry in your specific application between "user gets an incomplete answer" and "user waits slightly longer for a regenerated, more complete one."

## Practical pattern

Building the response-side guardrail agent, and deciding when a Storm-style dynamic architecture is warranted instead of a fixed graph:

1. run all four response-grounding checks — grounding, relevance, completeness, toxicity — as a standard final stage on every generated response before it reaches a user, regardless of what planning architecture produced it upstream;
2. decompose multi-part questions explicitly before checking completeness — checking the aggregate response against the whole question misses partial coverage the way a single embedding-similarity score against the full question can hide;
3. on a failed check, choose the recovery path based on the failure type: insufficient evidence (send back through exploratory search) versus adequate evidence handled poorly by generation (trigger regeneration with the same evidence, possibly with a corrective prompt);
4. before choosing between a LangGraph-style fixed-graph architecture and a Storm-style dynamic-planning architecture for a new project, honestly assess whether the problem's sub-structure (which agents/roles are needed, in what order) can be reasonably anticipated in advance — if genuinely not, a dynamic-planning approach isn't optional flexibility, it's a structural requirement for the problem to be solvable at all;
5. apply response grounding regardless of which planning architecture you chose — it's a downstream, generation-time check that both architectures need equally.

## Common traps

- checking relevance only against the full original query for multi-part questions, missing partial non-answers that a sub-question-level decomposition would catch;
- treating a failed grounding or completeness check as a dead end requiring the system to simply refuse or apologize, rather than as a signal that should route back into exploratory search or regeneration depending on the specific failure;
- forcing a genuinely open-ended, exploratory-planning problem into a LangGraph-style fixed graph because the team already knows the framework, producing the "workflow with a touch of AI" outcome the course explicitly warns against, rather than recognizing the problem needs Storm-style dynamic agent creation;
- assuming a Storm-style dynamically-planned system is exempt from response grounding because it's "more sophisticated" — dynamic planning addresses how the work gets organized, not whether the final generation step stays faithful to its evidence, which is an entirely separate failure mode requiring its own check.

## Takeaways

- A response-side guardrail agent should check grounding, relevance, completeness, and toxicity before any generated answer reaches a user — this is the last line of defense against failures that good retrieval and context engineering reduce but cannot eliminate on their own.
- Completeness checks require decomposing multi-part questions and checking each sub-question's coverage individually — an aggregate relevance score against the whole question can mask a silently dropped sub-question.
- Storm demonstrates a genuinely different agentic architecture from LangGraph: dynamically spawning topic-specific agents and a plan from scratch, rather than executing a pre-defined graph — the right choice when a problem's structure genuinely cannot be anticipated in advance, just as LangGraph is the right choice when it can.
