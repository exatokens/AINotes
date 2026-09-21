---
id: a1-07-memory-critique-reflection
title: "Memory, Critique, and Reflection: The Rubric for Reliable Agents"
week: 1
topic: "Act III: Reliability, Memory, and the Agentic World"
order: 7
summary: An agent without memory resembles a person with dementia, unable to build on prior context; critique and self-reflection exploit the fact that an LLM's discriminative ability usually exceeds its generative ability, giving agents a practical way to catch their own mistakes.
course: ai_agents
---

If the observe-reason-act loop is an agent's skeleton, memory and self-critique are the parts of its anatomy that keep it from being a very articulate amnesiac. An agent without memory is described in this week's material with a specific, uncomfortable comparison: it is like interacting with a person who has dementia — able to hold a fluent conversation in the moment, but unable to track what's already been tried, what's already been learned, or what the larger task even was five minutes ago.

Alongside memory sits a second, subtler design pattern that turns out to be disproportionately effective for reliability: asking an agent to critique or reflect on its own output before finalizing it. This exploits an asymmetry that is genuinely a little strange when you first hear it stated plainly — an LLM is often *better at spotting flaws in an answer* than it was at producing a flawless answer in the first place.

## Core intuition

Memory is the foundation of context and continuity: it lets an agent track what parts of a multi-step task are done, avoid repeating the same action, and personalize its behavior based on history. Critique and reflection are a cheap, practical way to convert an LLM's asymmetric strength — evaluation over generation — into better final answers, simply by giving the model a second pass at its own work before committing to it.

## Why it matters

Both patterns directly attack the two most common complaints about agentic systems: that they forget context mid-task, and that they hallucinate confidently. Memory addresses the first by giving the agent somewhere to record and retrieve progress. Critique and reflection address the second, not by making the underlying model less stochastic, but by spending a second round of inference specifically on the *judgment* task rather than the *generation* task, where LLMs are demonstrably stronger.

## Instructor framing

Draw the parallel to how software engineers actually work, since it's the exact analogy used in the source material: engineers asked to *produce* code often work quickly and make mistakes; the same engineers asked to *review* someone else's code apply far more scrutiny and catch far more. This isn't a moral failing unique to engineers — it's a structural fact about how attention and effort get allocated differently to generation versus evaluation tasks, and it transfers directly to LLMs.

## Worked example

Take a music-composition agent trained (via reinforcement learning and fine-tuning) as a master of Western classical composition, and now asked to compose a piece in the Hindustani classical tradition — a style it has no deep specialized training in. Two mechanisms rescue it. First, **memory in the form of RAG**: rather than trying to compose from pure parametric recall, it consults reference material on Hindustani ragas and structures — knowledge (RAG) supplementing reasoning (RL), exactly as the "musician learning on the fly" analogy in this week's material describes. Second, **critique and reflection**: after producing a first draft, the same model (or a paired "senior" agent) is asked to review the draft against the retrieved reference material — does this actually follow raga structure, or does it default to Western harmonic habits out of old habit? This second pass, specifically framed as *evaluation* rather than *composition*, catches errors the first pass's generative momentum missed. The simplest version of this whole pattern is the one-line prompt "can you do better?" — deceptively small, but it forces the model into a reflective mode that effectively doubles the compute spent on the answer and frequently yields a meaningfully improved result.

## Math explained step by step

The critique-and-reflection pattern has a clean cost-benefit structure worth making explicit, since "ask it to double-check" is not free — it's a second inference call, and the decision to spend that call should be principled.

**Step 1 — model the probability an initial answer is correct.** Let $p_1$ be the probability the agent's first-pass generative answer is correct (or adequately grounded).

**Step 2 — model the critique step's catch rate.** Let $q$ be the probability that, given an incorrect first answer, a critique pass correctly identifies it as flawed (this is the "discriminative ability" the source material claims is stronger than generative ability, so empirically $q$ tends to run higher than you'd naively expect from $p_1$ alone).

**Step 3 — model the revision step's success rate.** Let $r$ be the probability that, given a correctly identified flaw, the agent's revision actually fixes it (revision is itself a generative act and inherits some of the same first-pass error rate, so $r < 1$ in general).

**Step 4 — compute the two-pass accuracy and compare cost.** The probability of a correct final answer after one critique-and-revise cycle is $p_1 + (1-p_1)\cdot q \cdot r$ — strictly higher than $p_1$ whenever $q, r > 0$, at the cost of roughly doubling the inference calls per task (this is exactly the "doubling its computational budget" the source material notes). This is a clean, explicit trade: is the accuracy gain $(1-p_1)qr$ worth the doubled cost, for this particular task? For high-stakes or user-facing outputs, almost always yes; for cheap, low-stakes, high-volume calls, the arithmetic may say no.

## Practical pattern

1. Implement task memory explicitly (what steps are done, what's pending) for any agent performing a multi-step task — don't rely on an LLM's context window alone to substitute for structured state tracking.
2. Add a durable, RAG-backed memory layer for background knowledge (user preferences, prior interactions, domain reference material) the agent should recall across sessions, not just within one.
3. For any high-stakes generative output, add an explicit critique pass — either self-critique with a simple "can you do better, and specifically check X, Y, Z" prompt, or a paired supervisor-agent architecture (a "senior editor" reviewing an "editor," with a checklist of criteria the output must satisfy).
4. Budget for the doubled (or more) inference cost of critique loops deliberately — apply them where $(1-p_1) q r$ is worth it, not uniformly across every call the system makes.

## Common traps

- Building an agent with no explicit memory and expecting long-context windows alone to substitute for structured progress-tracking — this leads to repeated actions and lost context on genuinely long or interrupted tasks.
- Enabling default persistent memory (as in consumer products like ChatGPT) without surfacing clear user controls — this creates real privacy exposure, since stored interaction histories can become discoverable under legal process such as a subpoena.
- Treating self-critique as a magic fix rather than a probabilistic improvement — the math above shows it raises accuracy, it does not guarantee correctness, and a poorly designed critique prompt (vague, with no explicit checklist) yields a low catch rate $q$.
- Applying expensive critique loops uniformly to every call regardless of stakes, doubling cost across the board for marginal benefit on low-risk outputs.

## Takeaways

- Memory is not optional polish; without it, an agent cannot track multi-step progress or personalize behavior, and behaves like a fluent amnesiac.
- Critique and reflection exploit a genuine asymmetry — LLMs are often better evaluators than generators — turning a second inference pass into a real accuracy gain.
- The gain from a critique loop is quantifiable: $(1-p_1) \cdot q \cdot r$ additional correct answers, at roughly double the inference cost — a real trade-off to make deliberately, not a free lunch.
- Persistent memory carries real privacy and legal-exposure implications and needs explicit user control, not silent defaults.
