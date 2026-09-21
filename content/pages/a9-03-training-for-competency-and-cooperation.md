---
id: a9-03-training-for-competency-and-cooperation
title: "Training Has Two Jobs: Core Competency and Cooperation"
week: 9
topic: "Act I: The Escalation Ladder for Agent Intelligence"
order: 3
summary: Fine-tuning an agent for individual skill and fine-tuning it to cooperate with teammates are two different training goals requiring two different methodologies — and confusing them stalls multi-agent projects.
course: ai_agents
---

Two engineering primadonas on the same team will inevitably conflict — "the pond is too small for two big fishes" — no matter how individually excellent each one is. A famous Yankee coach once observed that hiring extraordinary players is easy; making them play together is extraordinarily hard. This is not a soft, people-management observation dressed up for an engineering course. It maps onto a hard fact about training methodology: the technique that makes an individual model excellent at its craft is often useless, or actively counterproductive, for making that model cooperate with others.

This page draws the line the course draws between Pillar 4's two halves — training for core competency, and training for cooperation — and explains why the second one, almost by necessity, drags in reinforcement learning where the first one can often get away with simple supervised fine-tuning.

## Core intuition

Training for **core competency** is like sending a cook to culinary school: you take a base model and instill a specialized, high-level skill — better grammar detection, sharper code review, more accurate diagnosis. This can frequently be done with **Supervised Fine-Tuning (SFT)**, because a "ground truth" exists: an imperfect output can be compared against a known-good one, and the loss computed directly.

Training for **cooperation** is a different animal. When multiple agents must "play well together," there often is no clean ground truth for the team's *collective* output — you cannot hand a supervised loss function a labeled example of "the correct way for five agents to divide this task." This absence of ground truth is what pulls cooperation training toward **Reinforcement Learning (RL)**: define a reward proportional to how well the team's joint output serves the goal, and let the agents find their own division of labor.

## Why it matters

Confusing these two training goals produces a specific, recognizable failure: a team fine-tunes each individual agent extensively for its own specialty — the SQL-writing agent gets very good at SQL, the QA agent gets very good at spotting bugs — and then wonders why the multi-agent system as a whole still misfires. The reason is that individual excellence was trained with SFT against individual ground truths, while the *cooperation* between the agents was never trained at all. Nobody optimized the handoffs, the division of responsibility, or the shared plan; those are Pillar 4's cooperation half, and it needs its own training signal, typically an RL-style reward on team-level outcomes.

## Instructor framing

This page is the conceptual hinge into the rest of the course's reinforcement-learning material. Every subsequent page on RL vocabulary, policy gradients, and reward design is, at bottom, in service of solving the credit-assignment problem this page raises: if a team's output is imperfect, how do you decompose that imperfection and assign blame to individual agents in order to perform gradient descent? Keep that question in mind through the escalation-ladder and RL-vocabulary pages that follow — it is the same unsolved problem, approached from increasingly rigorous angles.

## Worked example

Take a concrete competency-training task: correcting grammatical imperfections in a sentence. This has a clean SFT setup — feed the model an imperfect sentence, compare its output to a "perfect" ground-truth correction, compute cross-entropy loss, backpropagate. The exact same task can be reformulated for RL instead: define a reward proportional to how "proximal" the model's output is to the perfect answer, and optimize that reward. Both work here, because a ground truth exists either way.

Now consider training a three-agent culinary team (appetizer, main, dessert) to jointly produce a harmonious meal. There is no single labeled "correct" joint output to imitate — countless valid three-course combinations exist. SFT has nothing to regress against. But a reward function can still be defined: did the diners enjoy the meal, did the courses clash, was the meal delivered on time? RL can optimize against that reward even without a labeled ground truth, because RL only needs a scalar signal of how good the outcome was, not an example of the ideal one.

## Math explained step by step

Formalize why SFT needs ground truth and RL does not, and where the credit-assignment cost enters.

**Step 1 — SFT's loss.** For an individual competency task with input $x$ and ground truth $y$, the SFT loss is direct: $\mathcal{L}_{\text{SFT}} = -\log P_\theta(y \mid x)$, a well-defined, low-variance gradient signal computed per example.

**Step 2 — the missing term for teams.** For a team output $\hat{y}_{\text{team}} = f(a_1, a_2, \ldots, a_n)$ produced jointly by $n$ agents, there is generally no single labeled $y_{\text{team}}$ to regress against — the space of "good" joint outputs is too large and context-dependent to enumerate as training pairs.

**Step 3 — RL substitutes a scalar reward for a labeled target.** Define $R(\hat{y}_{\text{team}})$, a reward over the joint outcome (diner satisfaction, task success, timeliness). The training objective becomes $\max_{\theta_1, \ldots, \theta_n} \mathbb{E}[R(\hat{y}_{\text{team}})]$ — no per-agent ground truth is required, only an evaluable joint outcome.

**Step 4 — the price of this substitution is credit assignment.** Because $R$ is defined only over the joint output, the gradient contribution of any single agent $a_i$ is not directly observable — the reward doesn't say which agent's decision caused the good or bad outcome. This is exactly the **credit assignment problem**, and it is the reason RL for cooperation is described elsewhere in the course as computationally expensive and "rollout inefficient": you must run many joint episodes and statistically infer, rather than directly compute, each agent's contribution.

## Practical pattern

1. classify every training need as either "does this agent have a labeled ground truth to imitate?" (competency, likely SFT) or "am I evaluating a joint outcome with no single correct joint answer?" (cooperation, likely RL);
2. exhaust SFT for anything with usable ground truth before reaching for RL — SFT is faster to iterate, cheaper to run, and lower variance;
3. for cooperation training, invest first in reward design — a reward that only fires on rare full-team success is a much weaker signal than one with intermediate, per-stage reward shaping;
4. expect cooperation training to require substantially more rollouts (episodes) than competency training for the same amount of behavioral improvement, and budget compute accordingly.

## Common traps

- fine-tuning every individual agent to local perfection with SFT and assuming team-level performance will follow automatically — cooperation is a distinct, untrained skill;
- attempting to force cooperation training into an SFT mold by inventing an artificial "ground truth" joint output, which discards the genuine diversity of valid team behaviors and biases the system toward one narrow pattern;
- underestimating the cost of RL-based cooperation training — because credit assignment across agents is harder than within a single agent, expect more rollouts and more careful reward design than single-agent RL;
- treating "hire two of the best individual agents" as a strategy — as the primadona analogy warns, individual excellence without cooperation training can actively degrade team output.

## Takeaways

- Pillar 4 (training) splits into two distinct goals — core competency and cooperation — and they call for different methodologies.
- Core competency training usually has ground truth available and is well-served by Supervised Fine-Tuning.
- Cooperation training usually lacks a labeled joint ground truth and requires Reinforcement Learning against a scalar team-level reward.
- The price of RL's ground-truth-free flexibility is the credit assignment problem: attributing a joint reward back to individual agents' decisions, which the rest of the course's RL material exists to solve rigorously.
