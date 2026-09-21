---
id: a2-01-anatomy-of-an-agent
title: "The Anatomy of an Agent, Revisited"
week: 2
topic: "Act I: The Anatomy of an Agent"
order: 1
summary: An agent's five components — environment, goal, observation, reasoning, action — combine with a specific historical breakthrough in autonomous reasoning, without which the whole architecture stays theoretical.
course: ai_agents
---

Week one gave you the observe-reason-act loop as a shape. Week two's job is to explain why that shape sat mostly theoretical for decades, and what specifically changed to make it real. The honest answer is unglamorous: the loop's structure was well understood by researchers in distributed AI long before large language models existed. What was missing wasn't the architecture — it was the reasoning stage itself. Early systems could observe and act just fine. They could not genuinely *reason* about novel situations; at best they matched patterns from training data, which is a different thing wearing the same clothes.

This week reframes the agent's anatomy with that history in view, and it's worth taking the reframing seriously, because it changes what you should expect an agent to be capable of versus what you should still hardwire yourself.

## Core intuition

An agent is an autonomous observer, reasoner, and actor embedded in an environment, working toward a goal — five components, each doing distinct work: the environment defines the space of possible states, the goal defines what "done" looks like, observation is the perception mechanism, reasoning forms and revises a plan, and action executes that plan through available tools. What makes this genuinely agentic, rather than a fancy sensor-actuator loop, is that the reasoning component is capable of *autonomous* reasoning — analyzing a situation and forming a plan without following a pre-scripted decision tree.

## Why it matters

Distinguishing components matters because failures in an agentic system are almost always localizable to exactly one of these five, and the fix differs completely depending on which one is broken. A system with a bad goal specification fails differently, and needs a different fix, than a system with a broken observation channel (missing or noisy sensor data) or an under-powered reasoning component. Treating "the agent isn't working" as a monolithic problem, rather than diagnosing which of the five components is at fault, is a fast way to waste an engineering week.

## Instructor framing

Have students explicitly label each of the five components for every example encountered from here forward, including tricky boundary cases. A rules-based chatbot has an environment, a sort of goal, and an action mechanism — but if its "reasoning" is a lookup table or decision tree with no genuine autonomy, it fails the test, and that's fine to say plainly. The five-component breakdown is a diagnostic lens, not a checklist to pad every homework write-up.

## Worked example

Apply the five components to a vacuum-cleaning robot, since it's concrete enough to check your understanding against and appeared already in week one. Environment: the room's layout, furniture positions, and dust distribution — notably, not something the agent needs mapped in advance; it can explore. Goal: clean the room efficiently. Observation: cameras, dust sensors, proximity detectors. Reasoning: computing an efficient cleaning path even in an unfamiliar room — the genuinely agentic step, because a hardwired vacuum would need every room pre-mapped by its designer. Action: motors and suction executing the computed path. Now do the diagnostic exercise: if the vacuum keeps bumping into the same chair leg, is that an observation failure (proximity sensor miscalibrated), a reasoning failure (path planning ignoring known obstacles), or an action failure (motors not responding to steering commands as reasoned)? Each has a different fix, and none of them is solved by "add a bigger model."

## Math explained step by step

The historical breakthrough this week centers on — reinforcement learning inducing genuine reasoning rather than imitation — has a clean way to state what changed mathematically between "imitative" and "genuine" reasoning.

**Step 1 — formalize imitation-based reasoning.** An imitation-trained model approximates $\hat\pi(a|s) \approx \pi_{\text{demo}}(a|s)$ — it learns to mimic the action distribution of demonstrated examples $\pi_{\text{demo}}$ for states $s$ similar to ones it was shown. For states far outside the demonstrated distribution, $\hat\pi$ has no principled basis for choosing $a$ — this is the "monkey see, monkey do" pattern of early chain-of-thought prompting.

**Step 2 — formalize reward-induced reasoning.** A reinforcement-learning-trained model instead approximates $\pi^*(a|s) \approx \arg\max_\pi \mathbb{E}[\sum_t \gamma^t r_t \mid \pi]$ — it is trained to maximize expected cumulative reward $r_t$ across a trajectory, not to match any particular demonstrated action. Crucially, this objective is defined even for states never seen during training, because the model is optimizing toward an outcome, not copying a labeled example.

**Step 3 — see why this generalizes further than imitation.** Because $\pi^*$'s training signal comes from whether the *outcome* was good (reward achieved), not from matching a fixed reference trajectory, the model is free to discover strategies no demonstrator ever exhibited — this is precisely the mechanism behind AlphaGo's famous "Move 37," a move that scored well under $\pi^*$'s learned value estimate despite matching no human game in its training data.

**Step 4 — connect this to the "genuine reasoning" claim.** The 2025 breakthrough referenced across this week's material trained models on math and coding tasks with objectively verifiable rewards (correct answer or not), rather than demonstrating solutions step by step. Because the reward signal required no human-authored reasoning trace to imitate, the model was forced to develop its own internal search-and-verify process to reliably earn reward — which is what "spontaneous emergence of reasoning" means in precise terms: reasoning as an instrumentally necessary strategy for maximizing $\mathbb{E}[\sum_t \gamma^t r_t]$, not as a pattern copied from a labeled trace.

## Practical pattern

1. For any agentic system, explicitly write out its five components before writing any code — environment, goal, observation, reasoning, action — and identify which component is doing genuinely autonomous work versus which are mechanical (most observation and action stages are; the interesting engineering risk concentrates in reasoning).
2. When an agent misbehaves, diagnose by component before reaching for a bigger model or a longer prompt — a broken observation channel or a poorly specified goal will not be fixed by improving reasoning quality.
3. Prefer reasoning models trained with verifiable-reward-style objectives for tasks with a genuinely checkable outcome (math, code, structured data extraction) over prompting techniques that rely on imitating a demonstrated reasoning trace, since the former generalizes further off-distribution.
4. Reserve chain-of-thought-style worked examples in prompts for tasks where you specifically want the model to imitate a known-good procedure, not for tasks where you want it to discover a better one than any example you could write.

## Common traps

- Treating "reasoning" as a single monolithic capability rather than recognizing the qualitative difference between imitation-based pattern matching and reward-induced strategic reasoning.
- Diagnosing every agent failure as a "the model isn't smart enough" problem, when the actual fault often lies in observation quality, goal specification, or the action interface.
- Assuming a longer or more example-laden prompt always helps a reasoning-capable model — for genuinely reasoning models, an over-specified chain-of-thought example can shackle the model into a worse strategy than it would have found on its own.
- Forgetting that an agent's environment need not be fully known in advance — over-engineering elaborate pre-mapping or pre-enumeration when exploration-based reasoning would suffice.

## Takeaways

- An agent's five components — environment, goal, observation, reasoning, action — are separately diagnosable, and most real failures localize to exactly one.
- The historical breakthrough enabling genuine agents was reward-induced reasoning, not architectural novelty — the observe-reason-act loop was already understood; the reasoning stage previously lacked the capacity for genuine autonomy.
- Reward-based training generalizes beyond any specific demonstrated trace because it optimizes for outcomes, not imitation — this is mathematically why RL-trained models can discover strategies no human ever demonstrated.
- Chain-of-thought examples help imitation-style reasoning but can actively hurt genuinely reasoning-capable models by constraining them to a suboptimal, pre-specified path.
