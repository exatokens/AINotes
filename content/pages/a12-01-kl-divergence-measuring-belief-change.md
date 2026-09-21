---
id: a12-01-kl-divergence-measuring-belief-change
title: "KL Divergence: Measuring How Far a Policy Has Drifted"
week: 12
topic: "Act I: Trust Regions and the Reasoning Breakthrough"
order: 1
summary: KL divergence measures how much one probability distribution fails to look like another, derived from a simple coin-toss likelihood-ratio argument, and it becomes the mathematical tether that keeps policy updates from wandering too far from where they started.
course: ai_agents
---

Imagine two coins. Coin 1 is your reference, landing heads with probability $P_1$. Coin 2 is a suspect, landing heads with probability $Q_1 \ne P_1$. You toss a coin some large number of times and observe a sequence of heads and tails. A natural question: how much more likely is it that Coin 1 produced this evidence than Coin 2? That question, pushed through a few lines of algebra and a limit as the number of tosses goes to infinity, produces one of the most important quantities in modern machine learning — the Kullback-Leibler divergence — and it turns out to be exactly the tool needed to keep a reinforcement-learning policy from destroying itself mid-training.

This page derives KL divergence from that coin-toss argument rather than presenting it as a formula to memorize, because the derivation is what makes its asymmetry — a property that trips up nearly everyone the first time — feel inevitable rather than arbitrary.

## Core intuition

**KL divergence**, $D_{KL}(P \| Q) = \sum_i P_i \log\left(\frac{P_i}{Q_i}\right)$, measures how much evidence points toward reference distribution $P$ rather than test distribution $Q$ — equivalently, how much $Q$ "fails to look like" $P$. It is not a distance in the geometric sense: $D_{KL}(P\|Q) \ne D_{KL}(Q\|P)$ in general, which is why it's called a *divergence*, not a distance. This asymmetry is not a flaw or an approximation error — it falls directly out of the derivation, and it reflects something real: the "surprise" of observing $P$ when you expected $Q$ is not, in general, the same magnitude as the reverse surprise.

Contrast this with the **Wasserstein (Earth Mover's) distance**, which is symmetric by construction — it measures the physical work needed to reshape one pile of sand (distribution $P$) into another (distribution $Q$), and moving sand from $Q$-shape to $P$-shape costs the same as the reverse. KL divergence has no such guarantee, because it is fundamentally a statement about *evidence and likelihood*, not about physical rearrangement.

## Why it matters

KL divergence matters here because the algorithms covered in the rest of this week — TRPO, PPO, and ultimately DeepSeek's training recipe — all need a way to answer one specific question: how far has the new policy $\pi_\theta$ drifted from the old policy $\pi_{\text{old}}$ (or from the original pre-trained reference model $\pi_{\text{ref}}$)? KL divergence is the tool that answers it, because both $\pi_\theta$ and $\pi_{\text{old}}$ are themselves probability distributions (over next tokens, given a state) — exactly the kind of object KL divergence is built to compare.

## Instructor framing

Walk through the coin-toss derivation in full before naming the final formula — students who see $D_{KL}$ emerge as the limit of a likelihood-ratio argument, rather than encountering it cold, tend to retain both the asymmetry and the "measures surprise" intuition much more robustly than students handed the formula first. This derivation is also the natural moment to preview where KL divergence reappears later this week: as the "honey" in TRPO's trust region, and again as the anchor term in DeepSeek's GRPO loss.

## Worked example

Suppose Coin 1 is fair ($P_1 = 0.5$, $P_2 = 0.5$) and Coin 2 is heavily biased ($Q_1 = 0.9$, $Q_2 = 0.1$). If you toss a coin many times and observe roughly equal numbers of heads and tails — a mix consistent with a fair coin — the likelihood of Coin 1 producing this evidence vastly exceeds the likelihood of Coin 2 producing it, since Coin 2 "expects" heads nine times out of ten. Working the ratio through the algebra below shows this gap growing exponentially with the number of tosses, which is exactly the intuition KL divergence is built to formalize: it quantifies, per observation on average, how strongly the evidence favors one hypothesis over the other.

Now map this onto policy optimization directly: $\pi_{\text{old}}$ plays the role of Coin 1 (the reference), $\pi_\theta$ plays the role of Coin 2 (the candidate you're evaluating), and $D_{KL}(\pi_{\text{old}} \| \pi_\theta)$ measures how much the new policy's behavior would "surprise" an observer expecting the old policy's behavior — a small value means the new policy still behaves similarly to the old one on the actions that matter; a large value means it has drifted substantially.

## Math explained step by step

Derive $D_{KL}$ from the coin-toss likelihood ratio explicitly.

**Step 1 — write the likelihood ratio.** For $N_H$ heads and $N_T$ tails observed, the likelihood of Coin 1 producing this evidence is $P_1^{N_H} P_2^{N_T}$; the likelihood of Coin 2 producing it is $Q_1^{N_H} Q_2^{N_T}$. The ratio is $\dfrac{P_1^{N_H} P_2^{N_T}}{Q_1^{N_H} Q_2^{N_T}}$.

**Step 2 — normalize and take logs.** Raising to the $1/N$ power (normalizing for trial count) and taking the logarithm converts the product into a sum: $\frac{1}{N}\log\left[\frac{P_1^{N_H}P_2^{N_T}}{Q_1^{N_H}Q_2^{N_T}}\right] = \frac{N_H}{N}\log\frac{P_1}{Q_1} + \frac{N_T}{N}\log\frac{P_2}{Q_2}$.

**Step 3 — take the limit as $N \to \infty$.** By the law of large numbers, $\frac{N_H}{N} \to P_1$ and $\frac{N_T}{N} \to P_2$ (the *true* frequencies, since the evidence is genuinely generated by Coin 1). Substituting these limits gives exactly $D_{KL}(P\|Q) = P_1 \log\frac{P_1}{Q_1} + P_2\log\frac{P_2}{Q_2}$, which generalizes to any number of outcomes as $D_{KL}(P\|Q) = \sum_i P_i \log(P_i/Q_i)$.

**Step 4 — confirm the asymmetry directly from the derivation.** Notice that Step 3 specifically used the *true* frequencies converging to $P_1, P_2$ — this presumed $P$ is the reference generating the evidence. Swapping the roles ($Q$ as reference, $P$ as test) produces a genuinely different limiting expression, $D_{KL}(Q\|P) = \sum_i Q_i \log(Q_i/P_i)$, with no algebraic reason to equal the original — the asymmetry is baked into which distribution plays the role of "ground truth generating the evidence," not an artifact of notation.

## Practical pattern

1. when comparing two policies (old versus new, or current versus reference), use KL divergence rather than a symmetric distance metric — the asymmetry is meaningful here: $D_{KL}(\pi_{\text{old}}\|\pi_\theta)$ asks "how surprised would the old policy's expectations be by the new policy's behavior," which is the direction that matters for constraining *how far the new policy has moved*;
2. treat KL divergence as small-sample-friendly in the *local* regime — for small differences between distributions, KL divergence behaves approximately symmetrically, which is part of why it's usable as a practical constraint even though its exact asymmetry holds in general;
3. use KL divergence specifically when your two objects of comparison are themselves probability distributions over the same event space (like two policies' next-token distributions) — for objects better modeled as literal physical quantities needing reshaping (allocation problems, spatial distributions), Wasserstein distance is often the more natural tool;
4. remember that a KL divergence of zero means the two distributions are identical, and it grows without bound as $Q$ assigns near-zero probability to outcomes $P$ considers likely — a property worth checking for numerically (guard against $\log(0)$) in any implementation.

## Common traps

- treating KL divergence as symmetric and using $D_{KL}(P\|Q)$ and $D_{KL}(Q\|P)$ interchangeably — they are generally different quantities, and the direction chosen changes what the divergence actually measures;
- confusing KL divergence (an evidence/likelihood-based divergence) with a genuine distance metric like Wasserstein (a physical-transport-based distance) — they answer related but distinct questions and are not interchangeable substitutes;
- forgetting that KL divergence can blow up (diverge to infinity) when the test distribution $Q$ assigns zero or near-zero probability to an outcome the reference $P$ considers possible — a numerical hazard worth guarding against explicitly;
- treating KL divergence as an abstract statistics topic disconnected from RL, rather than recognizing it as the direct measurement tool the next two pages (TRPO and PPO) use to keep a policy update safely bounded.

## Takeaways

- KL divergence, $D_{KL}(P\|Q) = \sum_i P_i \log(P_i/Q_i)$, measures how much evidence favors reference distribution $P$ over test distribution $Q$, and falls directly out of a coin-toss likelihood-ratio argument taken to its infinite-sample limit.
- It is a divergence, not a distance — $D_{KL}(P\|Q) \ne D_{KL}(Q\|P)$ in general — and this asymmetry is a genuine, derivation-justified property, not an approximation artifact.
- Wasserstein distance offers a symmetric alternative built on physical transport cost, appropriate for a different class of comparison problems than KL divergence's evidence-based framing.
- KL divergence is the measurement tool the next pages use to constrain how far a new policy can drift from an old or reference policy during training — everything from TRPO's trust region to DeepSeek's anchoring term builds directly on it.
