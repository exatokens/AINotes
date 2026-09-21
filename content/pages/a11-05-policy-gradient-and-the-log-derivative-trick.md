---
id: a11-05-policy-gradient-and-the-log-derivative-trick
title: "From Consequence to Causation: The Log-Derivative Trick and REINFORCE"
week: 11
topic: "Act II: The Risks Beneath the Escalation Ladder"
order: 5
summary: You cannot differentiate a discrete outcome, but you can differentiate the continuous cause behind it — the log-derivative trick is the single identity that turns "make good tokens more likely" into a computable gradient, and it is the entire mathematical seed of REINFORCE.
course: ai_agents
---

Inside a rigged die, imagine a small steel ball suspended in jelly, free to sit anywhere along the die's interior. Move that ball smoothly and continuously — a tiny fraction of a millimeter at a time — toward the face opposite the "6," and at some point the die begins, ever so slightly, to favor landing on 6. The outcome of any single roll is still stubbornly discrete: you get a 6 or you don't, never a "5.8." But the *probability* of getting a 6 is a smooth, continuous function of the ball's position, and that continuous function is something calculus can act on even though the outcome itself never will be.

This is the entire trick behind training a language model with reinforcement learning, compressed into an object you can hold in your head. This page derives it properly — from the physical intuition, through the log-derivative identity, to the REINFORCE algorithm itself — because everything the weeks ahead build (PPO, GRPO, DeepSeek's training recipe) is a refinement of this one derivation, not a replacement for it.

## Core intuition

Language generation is fundamentally discrete: a token is "moon" or it is not, and there is no word that is "80% moon and 20% hammer" for the model to output as a compromise. You cannot compute a gradient of the *outcome* with respect to the model's parameters, because the outcome doesn't change smoothly as parameters shift — it stays constant, then snaps.

The resolution is to stop trying to differentiate the outcome and instead differentiate the **cause**: the continuous probability distribution the policy assigns over possible outcomes. Just as the steel ball's position (continuous) determines the die's outcome probabilities (also continuous, even though any single roll is not), a language model's parameters $\theta$ (continuous) determine $\pi_\theta(a \mid s)$, the probability of any given next token (also continuous). Optimize the continuous cause, and the discrete consequence follows.

## Why it matters

This reframing — from consequence to causation — is what makes gradient-based training of a discrete-output system possible at all. Without it, "reinforcement learning for language models" would be a category error: there would be nothing differentiable to optimize. With it, the entire machinery of gradient ascent becomes available, and the specific identity that makes the derivation tractable — the log-derivative trick — earns its place as one of the load-bearing pieces of mathematics in the whole field.

## Instructor framing

Walk through this derivation slowly and insist on the physical intuition (steel ball, sand bucket) sticking *before* introducing the symbols — students who can restate "we differentiate the cause, not the consequence" in their own words will find the algebra below almost inevitable rather than mysterious. This derivation is also the direct mathematical ancestor of PPO's clipped ratio and GRPO's group-relative advantage, both covered in later weeks — every one of those algorithms is, underneath its specific stabilization tricks, still computing some variant of the gradient derived here.

## Worked example

Picture a child's tiny vocabulary — three words and a punctuation mark: "Papu" (father), "Ma" (mother), "Godi" (lap, meaning "pick me up"), and "." (end of sentence). With four tokens and two-word sentences, there are $4 \times 4 = 16$ possible utterances (or $4^3 = 64$ if you count the terminal punctuation as a third slot). Picture each possible sentence as an empty bowl on the floor, and a single bucket of sand — representing total probability mass, which must sum to 1 — distributed among the bowls. If the father wants the child to say "Papu Godi" (father, pick me up), he cannot reach into the child's brain and flip a switch. He can only shift the environment — inch closer, dominate the child's field of view — smoothly biasing which bowl accumulates more sand over repeated attempts. This is gradient ascent, made physically visible: continuous nudges to a continuous quantity (sand distribution, or model parameters) that gradually favor one discrete outcome (a specific sentence, or a specific token) without ever touching the outcome directly.

## Math explained step by step

Derive REINFORCE properly, term by term.

**Step 1 — the log-derivative identity.** By the chain rule, $\frac{d}{d\theta}\log p(x) = \frac{1}{p(x)} \cdot \frac{dp(x)}{d\theta}$. Rearranged: $\nabla_\theta p(x) = p(x) \cdot \nabla_\theta \log p(x)$. This single identity — sometimes called "the rifle on the wall," introduced early because it becomes essential later — lets you rewrite the gradient of a probability as the probability itself times the gradient of its logarithm.

**Step 2 — set up the objective.** The training goal is $J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)] = \int P(\tau \mid \theta) R(\tau)\, d\tau$, the expected reward across all trajectories the current policy could generate. We want $\nabla_\theta J(\theta)$.

**Step 3 — apply the log-derivative trick to convert an intractable integral into an expectation.** Moving the gradient inside the integral gives $\nabla_\theta J(\theta) = \int \nabla_\theta P(\tau \mid \theta) \, R(\tau)\, d\tau$ — but differentiating a probability density directly is hard. Substituting the Step 1 identity, $\nabla_\theta P(\tau|\theta) = P(\tau|\theta)\nabla_\theta \log P(\tau|\theta)$, gives $\nabla_\theta J(\theta) = \int P(\tau|\theta) \nabla_\theta \log P(\tau|\theta) \, R(\tau)\, d\tau = \mathbb{E}_{\tau \sim \pi_\theta}\big[\nabla_\theta \log P(\tau|\theta) \, R(\tau)\big]$ — an *expectation*, which can be estimated by sampling actual trajectories, rather than an intractable integral.

**Step 4 — expand $\log P(\tau \mid \theta)$ and watch the environment drop out.** A trajectory's probability is a product over every step: $P(\tau \mid \theta) = P(s_0) \prod_t P(s_{t+1} \mid s_t, a_t) \cdot \pi_\theta(a_t \mid s_t)$. Taking the log turns this product into a sum, and taking the gradient with respect to $\theta$ kills every term that doesn't depend on $\theta$ — the initial state distribution $P(s_0)$ and the environment's transition dynamics $P(s_{t+1}\mid s_t, a_t)$ are both independent of the model's parameters, so their gradients are exactly zero. What survives is $\nabla_\theta \log P(\tau \mid \theta) = \sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t)$ — the gradient of the trajectory's log-probability reduces to a pure sum over the policy's own per-step log-probabilities, with no need to ever model the environment's dynamics at all.

**Step 5 — the final REINFORCE gradient.** Substituting back: $\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\Big[\Big(\sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t)\Big) R(\tau)\Big]$ — the 1992 result, due to Ronald Williams, that lets you estimate a usable gradient purely by sampling trajectories, computing how much each action's log-probability should move, and scaling that by the reward the whole trajectory received. High-reward trajectories push every action along the way to become more probable; low-reward trajectories push them to become less probable — no ground-truth label, no differentiable outcome, ever required.

## Practical pattern

1. when introducing policy-gradient methods to a team, lead with the steel-ball or sand-bucket intuition before any equation — the algebra is much easier to trust once "differentiate the cause, not the consequence" feels obvious rather than clever;
2. remember that the environment's transition dynamics genuinely drop out of the REINFORCE gradient — you never need a model of the environment to compute it, only samples of trajectories and their rewards, which is why this approach is called *model-free*;
3. treat REINFORCE's raw form as a starting point, not a production algorithm — its gradient estimate is high-variance because it scales every action's update by the same whole-trajectory reward $R(\tau)$, a limitation the credit-assignment and advantage-function material in later weeks directly addresses;
4. use this derivation as the reference point whenever a newer algorithm's math looks unfamiliar — PPO's clipped importance ratio and GRPO's group-relative advantage are both recognizable modifications of exactly the $\nabla_\theta \log \pi_\theta(a_t \mid s_t)$ term derived here, not unrelated inventions.

## Common traps

- trying to differentiate a discrete token or outcome directly, rather than the continuous probability the policy assigns to it — a category error the log-derivative trick exists specifically to route around;
- forgetting that the entire trajectory's reward $R(\tau)$ multiplies *every* per-step log-probability gradient equally in raw REINFORCE, which smears credit across good and bad actions alike within one trajectory — a limitation, not a feature, that motivates the advantage function covered in later weeks;
- assuming REINFORCE requires modeling the environment's dynamics, when Step 4 shows those terms drop out of the gradient entirely — this is precisely what makes it a model-free method;
- treating this derivation as historical trivia rather than as the literal mathematical skeleton underneath every modern RLHF, PPO, DPO, and GRPO variant covered in the weeks ahead.

One coda worth holding alongside the common traps above: because $R(\tau)$ is a single scalar assigned to an entire trajectory, and it multiplies the log-probability gradient of *every* action in that trajectory equally, a single lucky bad move embedded in an otherwise excellent trajectory gets reinforced right alongside every good move around it. This is the mathematical seed of the credit assignment problem — introduced with the mouse-cat-cheese story earlier in the course, and formalized precisely here as a property of the $R(\tau)$ term's scope. Solving it (advantage functions, per-step baselines, group-relative scoring) is the throughline connecting this derivation to essentially all of the next several weeks' material.

## Takeaways

- Language generation is discrete and non-differentiable, but the policy's probability distribution over tokens is continuous and fully differentiable — RL for LLMs works by optimizing that continuous cause, never the discrete consequence directly.
- The log-derivative trick, $\nabla_\theta p(x) = p(x)\nabla_\theta \log p(x)$, is the single identity that converts an intractable gradient of an expectation into a tractable expectation of a gradient, sampled from actual rollouts.
- The REINFORCE gradient, $\mathbb{E}_\tau\big[(\sum_t \nabla_\theta \log \pi_\theta(a_t\mid s_t)) R(\tau)\big]$, requires no model of the environment's dynamics — those terms provably drop out — which is why it is a model-free algorithm.
- Raw REINFORCE is high-variance because a whole trajectory's reward is applied uniformly to every action within it, smearing credit across good and bad steps alike — the exact problem the credit-assignment and advantage-function material in later weeks exists to fix.
