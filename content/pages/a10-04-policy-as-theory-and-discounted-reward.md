---
id: a10-04-policy-as-theory-and-discounted-reward
title: "The Policy as a Theory of the World, and Why Rewards Get Discounted"
week: 10
topic: "Act I: The Vocabulary of Reinforcement Learning"
order: 4
summary: A policy is the agent's internal theory of what action a state calls for, and discounting future rewards is the mathematical device that stops a policy from confusing a slow win with a fast one — or from looping forever to farm small rewards.
course: ai_agents
---

The same curved object lies across a forest path. One agent's internal theory identifies it as a snake and it bolts. A second agent's theory identifies the identical object as a rope and it walks over without concern. The external state — the object, the path, the light — did not change between the two agents. Only the internal theory did, and that internal theory alone determined the entire subsequent action. This is the cleanest possible illustration of what a "policy" actually is in reinforcement learning: not a lookup table of correct answers, but a theory of reality that causes behavior.

This page defines the policy formally and then addresses a question that trips up almost everyone encountering RL for the first time: if you have a sequence of small, per-step rewards, is the total reward for a trajectory just their sum? The answer is "almost, but not quite" — and the "not quite" is discounting, a small mathematical correction with large behavioral consequences.

## Core intuition

The **policy**, $\pi_\theta(a_t \mid S_t)$, is the agent's parameterized theory of which action a given state calls for — read as "the probability, under parameters $\theta$, of taking action $a_t$ given state $S_t$." Learning, in RL, *is* policy optimization: nudging $\theta$ so that the policy's implied behavior increasingly aligns with the reward structure of the environment.

Given a sequence of per-step rewards $r_1, r_2, r_3, \ldots$, the natural first guess for total trajectory reward is their plain sum. The correct formula instead applies a **discount factor** $\gamma \in (0, 1)$: $R = r_1 + \gamma r_2 + \gamma^2 r_3 + \cdots + \gamma^n r_n$. Rewards further in the future count for less.

## Why it matters

Discounting is not a cosmetic detail — it fixes two real pathologies that an undiscounted sum produces. First, it correctly prefers a *shorter* path to the same positive outcome: two trajectories that both eventually reach the cheese should not be valued equally if one gets there in three steps and the other in thirty, because the longer trajectory tied up more time and risk for the same eventual reward. Second, and more subtly, discounting prevents an agent from **gaming its own reward function** by looping indefinitely to farm small positive rewards rather than proceeding toward the actual goal — without discounting, an infinite loop of small positive rewards could sum to infinity and appear preferable to any finite, goal-completing trajectory, which is obviously not the behavior anyone intended to train.

## Instructor framing

Introduce the lottery analogy before the formula, because it makes the abstract "future value is worth less" claim land as common sense rather than as an arbitrary mathematical convention: winning a million-dollar lottery paid out over thirty years is not the same as a million dollars today, because a dollar thirty years out has diminished purchasing power — it is *discounted*. Once that's intuitive for money, the leap to "a reward ten steps from now is worth less than the same reward one step from now" requires no further persuading, and $\gamma$ can be introduced immediately afterward as simply the reward-space analogue of a financial discount rate.

## Worked example

Consider two mice reaching the same cheese. Mouse A starts at state $Y$, very close to the cheese, and reaches it in 2 steps: $r_1 = 0, r_2 = 10$. Mouse B starts further away, at state $X'$, and reaches the identical cheese in 8 steps, with all intermediate rewards zero and a final $r_8 = 10$. Without discounting, both trajectories sum to $R = 10$ — the formula would rate them identically, contradicting the intuition that starting closer to the goal is genuinely better (a claim the value-of-a-state page already established). With discounting at $\gamma = 0.9$: Mouse A's total is $R_A = 0 + 0.9 \times 10 = 9$; Mouse B's total is $R_B = 0.9^7 \times 10 \approx 4.78$. Discounting correctly separates the two, recovering the intuition that $V(Y) > V(X')$.

Now consider the runaway-loop failure mode directly: suppose an agent discovers it can repeatedly perform some minor, low-cost action that yields a tiny positive reward $\epsilon$ forever, instead of proceeding to the actual (larger, but one-time) goal reward. Undiscounted, an infinite sequence of $\epsilon$ rewards sums to infinity, which the optimizer would prefer over any finite goal reward — a clear misalignment between the *literal* reward specification and the *intended* one. With discounting, that same infinite loop sums to a finite geometric series, $\sum_{t=0}^{\infty} \gamma^t \epsilon = \frac{\epsilon}{1-\gamma}$, which is bounded and, for reasonable $\gamma$ and small $\epsilon$, easily beaten by pursuing the actual goal — discounting closes off the exploit.

## Math explained step by step

Derive the geometric-series bound that makes the loop-farming argument precise.

**Step 1 — write the discounted return.** $R = \sum_{t=1}^{n} \gamma^{t-1} r_t$, with $\gamma \in (0, 1)$ strictly less than 1.

**Step 2 — bound the infinite-loop case.** If an agent farms a constant small reward $\epsilon > 0$ forever instead of terminating, its discounted return is the geometric series $R_{\text{loop}} = \sum_{t=0}^{\infty} \gamma^t \epsilon = \frac{\epsilon}{1 - \gamma}$ — finite for any $\gamma < 1$, in sharp contrast to the undiscounted case where this sum diverges to infinity.

**Step 3 — compare against a one-time goal reward.** If the actual goal yields a one-time reward $G$ achievable in $m$ steps, its discounted value is $R_{\text{goal}} = \gamma^{m-1} G$. The loop is preferred by the optimizer only if $\frac{\epsilon}{1-\gamma} > \gamma^{m-1}G$ — a condition an engineer can check directly, and can rule out by choosing $\gamma$ appropriately relative to $\epsilon$, $G$, and $m$ (typically, keeping $\epsilon$ small and $\gamma$ not too close to 1 relative to the goal's value makes the loop unattractive).

**Step 4 — interpret $\gamma$ as a design knob, not a fixed constant.** $\gamma$ close to 0 makes the agent extremely myopic (only the very next reward matters, encouraging short-sighted behavior); $\gamma$ close to 1 makes the agent extremely far-sighted (patient, willing to sacrifice short-term reward for long-term gain, but also more vulnerable to the loop-farming pathology if the reward function has any exploitable small positive rewards). A typical value like $\gamma = 0.9$ or $0.99$ is a deliberate compromise, tuned per problem, not a universal default.

## Practical pattern

1. always discount multi-step rewards in any RL formulation — treat an undiscounted sum as a red flag rather than a simplification, since it opens the door to both the shorter-path-indifference problem and the infinite-loop-farming exploit;
2. audit your reward function specifically for any small, repeatable, low-cost positive reward before training — this is precisely the shape of reward that gets exploited by loop-farming if $\gamma$ is not tuned to discourage it;
3. treat $\gamma$ as a tunable hyperparameter reflecting how patient you want the agent to be, and validate empirically that your chosen $\gamma$ actually prefers the intended shorter, goal-directed trajectories over any exploitable alternative;
4. when debugging a policy that behaves oddly (looping, dawdling, taking unnecessarily long routes to a known-good outcome), check the discount factor and the reward shape before assuming the policy-learning algorithm itself is broken.

## Common traps

- treating "total reward" as a plain sum of per-step rewards without discounting, which silently opens the door to reward-hacking via infinite or extended loops;
- setting $\gamma$ too close to 1 in an environment with any exploitable small positive reward, inadvertently making loop-farming attractive relative to reaching the actual goal;
- setting $\gamma$ too close to 0 and producing a pathologically short-sighted policy that sacrifices genuinely valuable long-term outcomes for negligible immediate reward;
- forgetting that the policy is a *theory*, not a fixed lookup table — a policy trained under one reward or discount structure will not automatically generalize its behavior correctly if that structure changes without retraining.

## Takeaways

- A policy $\pi_\theta(a \mid s)$ is the agent's internal, parameterized theory about which action a state calls for — the same external state can produce opposite behavior under two different policies, exactly as the snake-versus-rope framing illustrates.
- Discounting future rewards by $\gamma^{t-1}$ per step, rather than summing rewards plainly, correctly prefers shorter paths to the same outcome and closes off infinite-loop reward-farming exploits.
- The choice of $\gamma$ is a deliberate design decision trading off myopia against far-sightedness, and it interacts directly with whether a given reward function is exploitable.
- Learning in RL is precisely policy optimization: adjusting $\theta$ so the agent's theory of the world increasingly produces high-discounted-return behavior.
