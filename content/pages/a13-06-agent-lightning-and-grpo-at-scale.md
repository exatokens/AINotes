---
id: a13-06-agent-lightning-and-grpo-at-scale
title: "Agent Lightning: Automatic Tracing, Equal Credit, and GRPO for Real Agents"
week: 13
topic: "Act I: Coordinating Many Minds"
order: 6
summary: Agent Lightning turns any agent's execution into RL training data automatically, uses a deliberately crude equal-credit strategy that the law of large numbers cleans up statistically, and GRPO's group-relative normalization keeps training stable when a single agent juggles wildly different reward scales.
course: ai_agents
---

The previous page's compounding-probability arithmetic explains *why* untrained agents fail roughly 70% of the time on realistic multi-step tasks; it does not, by itself, explain how to fix it. Simply collecting more demonstration data and running supervised fine-tuning helps only partially, because SFT teaches "what to do" from success paths and rarely teaches "what not to do" — without deliberately curated failure examples, the model never learns what to avoid. This page covers the specific, practical machinery — Microsoft's Agent Lightning framework and Group Relative Policy Optimization applied at the level of full agent trajectories — that converts the previous page's diagnosis into a genuine remedy, closing the gap from roughly 30% to reported figures upwards of 90% success on the same class of task.

## Core intuition

**Agent Lightning**'s core innovation is **automatic tracing**: instrumenting an agent application so that every tool call, every LLM prompt, and every response is captured automatically as a structured trajectory, the way application-performance-monitoring tools like AppDynamics trace code execution in a JVM without the developer writing manual logs. This removes the single largest practical barrier to training agents with RL — the tedious, error-prone work of manually collecting and structuring rollout data — by making trajectory capture a property of the framework, not a separate engineering project.

Once trajectories (successes and failures alike) are captured at scale, Agent Lightning applies a deliberately simple **Equal Credit Strategy** for credit assignment: if a trajectory succeeds (reward = 1), every step in that trajectory is reinforced equally; if it fails (reward = 0), every step is penalized equally. This sidesteps the hard problem of pinpointing which specific step deserves credit or blame — a version of the credit-assignment problem this course has returned to repeatedly — by relying instead on volume and statistics to sort it out.

## Why it matters

The Equal Credit Strategy sounds naively crude on first hearing — surely a bad intermediate step inside an otherwise-successful trajectory shouldn't get reinforced just because the trajectory happened to succeed anyway. The resolution is genuinely statistical, not a hand-wave: run hundreds of trajectories, and a truly bad step will appear disproportionately often in *failed* trajectories relative to successful ones, while a genuinely necessary, logical step will appear consistently across successful runs and comparatively rarely in failed ones. Over enough trajectories, the law of large numbers does the fine-grained credit assignment that no single trajectory's reward signal could do alone — the same fundamental idea behind GRPO's group-relative scoring from Week 12, now applied at the level of full multi-step agent trajectories rather than single-turn model outputs.

## Instructor framing

Connect this page explicitly back to Week 12's DeepSeek/GRPO material — the underlying insight is identical, only the unit of analysis has changed. There, the "group" was a set of candidate single-turn outputs for one prompt, scored by correctness and normalized by group Z-score. Here, the "group" is a set of full multi-step agent trajectories attempting the same task, scored by end-to-end success, with credit distributed via the deliberately coarse Equal Credit rule rather than a per-step Z-score. Both approaches share the same underlying bet: that statistical volume across many samples can substitute for a precise, per-unit credit-assignment mechanism that would otherwise be intractable to compute directly.

## Worked example

Return to the flight-booking task from the previous page to see the full pipeline in action. The developer defines success mechanically and unambiguously: a trajectory that books a ticket at or under $800 receives reward 1.0; any trajectory that fails, or that ignores the price constraint, receives reward 0 (or a penalty) — a verifiable reward, in the spirit of Week 12's DeepSeek approach, avoiding the reward-hacking risk a learned proxy reward model would introduce. The system synthesizes the task repeatedly and lets the agent attempt it hundreds of times; because the LLM's reasoning steps are stochastic, these hundreds of attempts produce a genuinely varied dataset — some successes, some failures with recognizable patterns (wrong price, hallucinated completion, forgotten constraint) — all captured automatically via Agent Lightning's tracing, with no manual data-collection effort required. This automatically-generated dataset, containing both successes and failures, trains the underlying model (typically via LoRA, for efficiency) using the Equal Credit Strategy, and reported results show accuracy climbing from the roughly 30% baseline to upwards of 90% — the model genuinely internalizing the logic of the domain rather than merely memorizing specific successful scripts.

**Group Relative Policy Optimization**, applied at scale across many different task types simultaneously, addresses a further practical wrinkle: different tasks naturally have wildly different native reward scales — a binary success/failure task (reward 0 or 1), a negotiation task scored 0 to 300, and a revenue-generation task scored 0 to 1000, for instance. Feeding these raw, unnormalized rewards directly into one shared optimizer would let the highest-magnitude task dominate every gradient update, causing the model to effectively ignore the lower-reward-scale tasks — a mode collapse across the task portfolio, not within any single task. GRPO's fix, exactly as in Week 12, is to generate multiple trajectories per prompt and normalize each trajectory's reward against its own group's mean and standard deviation before using it in training — a score of 0.8 on a 0–1 task and a score of 250 on a 0–300 task can then be compared on equal footing, because both are expressed as a Z-score relative to their own task's group, not as raw magnitudes.

## Math explained step by step

Formalize why raw multi-task reward scales cause mode collapse, and confirm GRPO's normalization fixes it — the multi-task extension of Week 12's single-task derivation.

**Step 1 — the raw-reward gradient magnitude problem.** In a standard policy-gradient update, the magnitude of the parameter update from a given trajectory scales with the magnitude of its reward signal: $\Delta\theta \propto \nabla_\theta \log \pi_\theta(\tau) \cdot R(\tau)$. If Task C's rewards range up to 1000 while Task A's range up to 1, a single Task C trajectory can produce a gradient contribution orders of magnitude larger than many Task A trajectories combined, purely as an artifact of reward scale, not of Task C's actual importance or difficulty.

**Step 2 — see the resulting mode collapse.** Because gradient descent (or ascent) follows the largest available signal, training dominated by Task C's large-magnitude rewards will preferentially improve Task C performance while Task A's smaller-magnitude gradient signal is comparatively drowned out — the model appears to be "ignoring" Task A, not because it's harder, but because its raw reward scale is smaller.

**Step 3 — apply group-relative normalization per task.** For each task type, generate a group of trajectories $\{o_1, \ldots, o_n\}$ for the *same* task instance, and compute each one's advantage as its Z-score within that task's own group: $A_i = \frac{r_i - \mu_{\text{task}}}{\sigma_{\text{task}}}$. This produces a dimensionless, scale-free quantity for every task, regardless of whether that task's raw rewards range over 0–1 or 0–1000.

**Step 4 — verify the fix restores balanced gradient contribution.** Because every task's advantage is now expressed in the same normalized (Z-score) units, a well-performing trajectory on Task A and a well-performing trajectory on Task C contribute comparably-sized gradient updates — the training process treats "did notably better than this task's own average" as the signal, not "produced a numerically larger reward," which is exactly the property needed to prevent one high-magnitude task from starving the others of learning signal.

## Practical pattern

1. instrument agent applications with automatic tracing (Agent Lightning or an equivalent tool) from the start of any RL-training initiative — manual trajectory collection is a large, avoidable engineering cost that automatic tracing eliminates almost entirely;
2. use a deliberately simple credit-assignment rule (Equal Credit or similar) when running enough trajectories per task to let statistical volume do the fine-grained attribution — this is often more practical than engineering a precise per-step credit-assignment mechanism directly;
3. define rewards mechanically and verifiably wherever the task allows (a price threshold met, an API call's return value checked), rather than relying on a model's own natural-language claim of success — directly closing the Hallucinating Agent failure mode from the previous page;
4. whenever training across multiple task types with different native reward scales, apply group-relative (GRPO-style) normalization per task before combining gradients — never feed raw, differently-scaled rewards into one shared optimizer without this step.

## Common traps

- attempting to hand-engineer precise per-step credit assignment for every agent trajectory, when a much simpler equal-credit rule, combined with sufficient trajectory volume, achieves comparable results at far lower engineering cost;
- collecting only successful trajectories for training data, missing the "what not to do" signal that a dataset including failures provides — SFT's structural blind spot that trajectory-level RL training with both successes and failures directly addresses;
- training across multiple tasks with different native reward scales without normalizing per task, inadvertently letting the highest-magnitude task dominate every gradient update while other tasks stagnate;
- trusting a model's self-reported success as the reward signal rather than mechanically verifying the underlying action actually occurred — reintroducing exactly the Hallucinating Agent risk this whole training pipeline is meant to eliminate.

## Takeaways

- Agent Lightning's automatic tracing converts ordinary agent execution into structured RL training data with no manual data-collection effort, capturing both successes and failures at scale.
- The Equal Credit Strategy deliberately avoids precise per-step credit assignment, relying instead on statistical volume across hundreds of trajectories to let genuinely necessary steps and genuinely harmful steps sort themselves out by their differential appearance in successful versus failed runs.
- GRPO's group-relative normalization, applied per task type, prevents high-magnitude-reward tasks from dominating training and starving lower-magnitude-reward tasks of learning signal — the same underlying mechanism as Week 12's single-task GRPO, generalized across a multi-task portfolio.
- This combination — automatic tracing, verifiable rewards, equal-credit assignment, and group-relative normalization — is what converts the previous page's ~30% untrained-agent baseline into reported real-world results upwards of 90%, by training directly for trajectory-level reliability rather than relying on prompting or SFT alone.
