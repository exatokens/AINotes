---
id: a12-05-deepseek-r1-and-grpo
title: "DeepSeek-R1: Reasoning from Pure RL, and Group Relative Policy Optimization"
week: 12
topic: "Act I: Trust Regions and the Reasoning Breakthrough"
order: 5
summary: DeepSeek-R1-Zero dropped the reward model and the SFT warm-start entirely, rewarding only verifiable correctness on math and code, and GRPO's group-relative Z-score let reasoning emerge from pure reinforcement learning rather than imitation.
course: ai_agents
---

For years the industry's working assumption was that inducing reasoning meant showing a model enough worked examples of thinking — chain-of-thought data, millions of problem-solution pairs with the intermediate steps spelled out — until the model absorbed the pattern. This produced something that looked like reasoning but was closer to sophisticated pattern-matching: a model could reproduce familiar reasoning shapes but remained brittle outside its training distribution, notoriously unable to count the letters in "strawberry" correctly despite having ingested a training corpus outweighing any human's total reading many times over. DeepSeek-R1-Zero's central, quietly revolutionary sentence was that a model trained via large-scale RL, with no supervised fine-tuning step at all, could develop reasoning behavior on its own. This page works through how that was actually achieved, and the specific optimization algorithm — GRPO — that made it economical.

## Core intuition

DeepSeek eliminated the reward-hacking vulnerability from the previous page's RLHF pipeline by a structural choice: **verifiable rewards**. Instead of training a learned reward model to approximate human preference (an imperfect proxy, as the previous page derived), DeepSeek restricted its RL training to domains with an absolute, checkable ground truth — mathematics (the answer is correct or it isn't) and coding (the code passes its unit tests or it doesn't). No neural reward model is required, and consequently there is no reward model to hack.

To process these rewards efficiently without a value-function critic, DeepSeek used **Group Relative Policy Optimization (GRPO)**: for each input query, the model generates a *group* of $n$ different candidate outputs $\{o_1, \ldots, o_n\}$, each scored for correctness, and each output's advantage is computed as its Z-score relative to the group: $A_i = \frac{r_i - \mu}{\sigma}$, where $\mu$ and $\sigma$ are the group's mean and standard deviation of reward. This is "grading on a curve" — the model learns from the *relative* difference between its better and worse attempts on the same problem, not from any absolute external critic.

## Why it matters

Removing the reward model removes an entire class of failure this course has spent time on: there is no proxy to drift away from, no plausibility-over-correctness gap to exploit, because "correct" is checked mechanically, not predicted by a fallible neural network. And GRPO's group-relative scoring removes the need for a separately trained critic network estimating $V(s)$ — instead, the group of samples generated for the *same* prompt serves as its own baseline, a cheap and directly comparable reference, since all $n$ outputs faced the identical problem.

## Instructor framing

The most pedagogically important structural choice in this whole story is the training format: the model's output was constrained to two XML tags, `<thinking>` and `<answer>`, with the reward function checking only two things — was the structure followed, and is the content of `<answer>` correct. Crucially, the *content* of `<thinking>` was never graded, never supervised, never even inspected by the reward function — it was a scratchpad the model could fill with anything, or nothing, entirely of its own choosing. Emphasize to students that reasoning was not demonstrated, taught, or rewarded directly; only the final answer's correctness was rewarded, and the model *itself* discovered, unprompted, that filling the scratchpad with extended deliberation was a winning strategy — this is the "unreasonable effectiveness of reinforcement learning" argument made concrete and falsifiable, not a rhetorical flourish.

## Worked example

The self-evolution process observed in DeepSeek-R1-Zero's training is worth walking through directly, because it is one of the field's cleanest documented instances of emergent behavior from RL. As training progressed, the average length of content inside the `<thinking>` tags grew — not because anyone instructed it to, but because the model discovered, purely through reward feedback, that longer deliberation correlated with more `<answer>` tags being marked correct. This growth was accompanied by specific, recognizable behaviors nobody explicitly programmed: **self-reflection** (looking back at its own previous reasoning tokens), **self-correction** (verifying its own intermediate steps), and **strategy exploration** (trying one approach, recognizing it wasn't working, and pivoting). The paper documents a specific "aha moment" in an intermediate checkpoint: mid-generation, on a problem the model was struggling with, the text flags an explicit realization of a flaw in its own approach, re-evaluates, and finds the correct path — a moment of insight the researchers report finding as striking as anyone reading the transcript would.

A companion release, DeepSeek-R1, addresses R1-Zero's practical rough edges — the raw model, while powerful, suffered from poor readability and language mixing (a form of the mode-collapse risk covered two weeks ago, here surfacing as a side effect of pure RL rather than aggressive SFT). R1 layered in multi-stage training and cold-start data to "civilize" this raw capability without discarding the reasoning it had discovered, and the resulting reasoning ability was successfully distilled into smaller open models like Qwen and Llama, transferring grandmaster-level reasoning behavior into much more widely deployable architectures.

## Math explained step by step

Derive the GRPO advantage and connect it to the general policy-gradient framework from the previous pages.

**Step 1 — generate a group of candidates.** For a single input $x$ (a math problem), sample $n$ complete outputs $\{o_1, \ldots, o_n\}$ from the current policy, each independently scored for correctness, giving raw rewards $\{r_1, \ldots, r_n\}$.

**Step 2 — compute group statistics.** Compute the group mean $\mu = \frac{1}{n}\sum_i r_i$ and standard deviation $\sigma = \sqrt{\frac{1}{n}\sum_i (r_i - \mu)^2}$.

**Step 3 — compute each output's advantage as its Z-score.** $A_i = \frac{r_i - \mu}{\sigma}$ — an output scoring above the group average gets a positive advantage (reinforced), one scoring below gets a negative advantage (suppressed), and the magnitude reflects how far above or below the group's own performance that specific attempt fell.

**Step 4 — plug this advantage into the PPO-style clipped objective from two pages ago.** GRPO's training loss combines this group-relative advantage with the same clipped-ratio machinery already derived for PPO, plus a KL-divergence penalty against the *reference* (original pre-trained) policy — the same anchoring choice flagged in the TRPO page as favored by modern systems specifically to strongly tether reasoning capability against long-run drift. The result balances two forces directly analogous to the fluctuation-dissipation framing used elsewhere in this material: the clipped PPO term drives exploration around the current policy (fluctuation), while the KL-to-reference term pulls back toward the original model's foundation (dissipation) — together preventing the training from either stagnating or destabilizing.

**Step 5 — why this substitutes cleanly for a learned critic.** A standard actor-critic setup needs a separately trained value function $V(s)$ to compute an advantage $A = R - V(s)$; GRPO instead uses the *group itself* as an empirical, directly-computed baseline — no separate network to train, no additional proxy to potentially miscalibrate, and a computation that is essentially free once the group's outputs and their (verifiable) rewards already exist.

## Practical pattern

1. wherever a task has a mechanically verifiable success criterion (unit tests pass, a computed answer matches, a formal proof checks), prefer a verifiable reward over a learned reward model — it removes an entire category of reward-hacking risk documented in the previous page;
2. use group-relative (GRPO-style) scoring when generating multiple candidate outputs per input is cheap, as it removes the need to train and maintain a separate critic network while still supplying a well-calibrated, per-input advantage signal;
3. give the model an ungraded scratchpad (structurally, not just informally) when you want reasoning behavior to emerge — DeepSeek's result specifically depended on *not* supervising the `<thinking>` content, only the final structured answer;
4. anchor long RL training runs with a KL penalty against the original pre-trained reference model, not merely the immediately preceding checkpoint, when the goal is preserving foundational capability over an extended, high-volume training process.

## Common traps

- assuming reasoning must be explicitly demonstrated or supervised to be trained into a model — DeepSeek-R1-Zero is direct evidence that pure outcome-based RL, with an entirely unsupervised scratchpad, can induce emergent reasoning behavior on its own;
- deploying a raw, pure-RL-trained model like R1-Zero directly into a user-facing product without the readability and language-consistency cleanup that R1's additional training stages specifically addressed;
- reaching for a learned reward model out of habit when the task actually has a mechanically verifiable success criterion available — this discards a real opportunity to eliminate an entire class of reward-hacking risk;
- treating GRPO's group-relative advantage as merely a computational shortcut, missing that it is a genuine alternative to critic-based advantage estimation with its own distinct trade-offs (it requires generating multiple samples per input, which raw actor-critic methods do not).

## Takeaways

- DeepSeek-R1-Zero trained reasoning through pure reinforcement learning against verifiable rewards (math and code correctness), with no supervised fine-tuning warm-start and no learned reward model — removing reward-hacking risk by construction.
- GRPO replaces a trained critic with a directly-computed, group-relative Z-score advantage: generate several outputs per input, score them, and reward each relative to the group's own mean and spread.
- Emergent reasoning behaviors — self-reflection, self-correction, strategy pivots, and a documented "aha moment" — arose from rewarding only final-answer correctness while leaving the model's scratchpad entirely unsupervised, strong evidence that reasoning can emerge from outcome-based RL rather than requiring direct imitation.
- Pure-RL training (R1-Zero) produced powerful but rough output (poor readability, language mixing); a follow-up training stage (R1) civilized this without discarding the underlying reasoning capability, and that capability was successfully distilled into smaller, more deployable open models.
