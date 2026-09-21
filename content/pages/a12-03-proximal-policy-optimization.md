---
id: a12-03-proximal-policy-optimization
title: "Proximal Policy Optimization: Tiny Feet Instead of Exact Trust Regions"
week: 12
topic: "Act I: Trust Regions and the Reasoning Breakthrough"
order: 3
summary: PPO keeps TRPO's stabilizing intuition but replaces its expensive exact KL constraint with a cheap clipped probability ratio — tiny feet instead of precise geometry — and that simplification is what made it the algorithm that actually trained ChatGPT.
course: ai_agents
---

TRPO solves the instability problem correctly but expensively — enforcing an exact KL-divergence trust region requires a conjugate-gradient solve on every single update, a computational tax that becomes brutal at the scale of a modern language model. Proximal Policy Optimization exists because a research team asked a pragmatic question: can we get *most* of TRPO's stabilizing effect with a much cheaper mechanism? The answer, and the reason PPO is the algorithm that actually trained the model behind ChatGPT rather than TRPO itself, is a simple clipping operation applied directly to the probability ratio — no KL computation, no conjugate gradients, just an inequality check on a single number.

## Core intuition

Instead of drawing a precise KL-divergence boundary around the old policy, PPO gives the agent "tiny feet": it directly limits how much the probability ratio $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\text{old}}(a_t|s_t)}$ is allowed to move in a single update, by clipping it to the range $[1-\epsilon, 1+\epsilon]$ for a small $\epsilon$ (commonly around 0.1–0.2). The PPO clipped objective is:

$$\mathcal{L}_{\text{PPO}} = \mathbb{E}_t\left[\min\left(r_t(\theta) A_t,\ \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\, A_t\right)\right]$$

If the ratio tries to move outside that band — the model attempting to drastically increase or decrease the probability of some action in a single step — the gradient contribution from that term is clipped, and the update simply stops rewarding further movement in that direction.

## Why it matters

This connects directly back to the sand-bucket picture from earlier this course: if the desired word is "Moon," you want to pile more sand into that bowl — increase its probability. PPO's contribution is the instruction "don't pile too much sand onto Moon in one step." That single constraint, applied uniformly and cheaply across every action in every trajectory, turned out to be sufficient to prevent the catastrophic instability that unconstrained policy gradient methods suffer from, without ever computing a KL divergence explicitly. This simplicity — a clip operation instead of a constrained optimization — is precisely why PPO, not TRPO, became the algorithm actually deployed at the scale required to train ChatGPT via RLHF.

## Instructor framing

Present the $\min(\cdot, \cdot)$ structure of the PPO objective as a deliberate pessimism, not an accident: taking the minimum of the unclipped and clipped terms means that whenever clipping would have made the objective look *better* than it should (by preventing a penalty for an excessive update), the algorithm instead uses the smaller, more conservative unclipped value — clipping only ever removes an *incentive* to over-update, it never manufactures an artificial bonus for doing so. This asymmetry is worth deriving explicitly with a worked numeric example, because it's the detail most easily glossed over and most likely to trip up an implementation.

## Worked example

Suppose the desired action is generating "moon" after "The cow jumped over the," and the current advantage estimate $A_t$ for this action is positive (it was a good choice). If the new policy increases the probability of "moon" modestly, $r_t(\theta) = 1.15$, this sits within a typical clip range of $[0.8, 1.2]$ (for $\epsilon = 0.2$), so the unclipped and clipped terms coincide, and the update proceeds with its full, unclipped gradient — a normal, sanctioned improvement.

Now suppose the new policy tries to increase the probability of "moon" aggressively, $r_t(\theta) = 1.5$, based on a single batch's advantage estimate. The clip function caps this at $1.2$ for the *clipped* term; since $A_t > 0$, $\text{clip}(r_t,\ldots)A_t = 1.2 A_t < r_t A_t = 1.5A_t$, so the $\min(\cdot,\cdot)$ selects the smaller, clipped value — the objective no longer rewards pushing the ratio further past $1.2$, and the gradient with respect to $\theta$ in that region is effectively flattened. The model is still allowed to move the probability, just not further than the tiny-feet bound permits in this single step; a well-supported further increase can still happen gradually, across subsequent updates, each one bounded the same way.

## Math explained step by step

Verify the asymmetric-pessimism claim about the $\min$ operator directly, since it is easy to state incorrectly.

**Step 1 — case $A_t > 0$ (the action was good).** Here we want to increase $r_t$. The clip caps $r_t$'s contribution at $1+\epsilon$ from above but does not restrict it from below $1-\epsilon$. If $r_t > 1+\epsilon$ (over-committing to a good action), $\min(r_t A_t, (1+\epsilon)A_t) = (1+\epsilon)A_t$ — the clipped, smaller value is used, removing the incentive to over-commit further. If $r_t < 1+\epsilon$, the clip doesn't bind, and the raw $r_t A_t$ is used unchanged.

**Step 2 — case $A_t < 0$ (the action was bad).** Here we want to decrease $r_t$. Because $A_t$ is negative, multiplying by a smaller $r_t$ produces a *larger* (less negative) product. If $r_t < 1-\epsilon$ (already strongly suppressing the bad action), $\min(r_t A_t, (1-\epsilon)A_t)$ selects $r_t A_t$, the *more negative* of the two — since $r_t A_t < (1-\epsilon)A_t$ when $r_t < 1-\epsilon$ and $A_t<0$ — meaning the raw, unclipped (larger-penalty) term is used, not the clipped one.

**Step 3 — the pattern across both cases.** In both cases, the $\min$ operator selects whichever term more conservatively resists an *excessive* move in the direction the advantage sign favors — it never selects a term that would grant extra credit for having moved too far. This is the precise sense in which PPO's clipping is a strict pessimism, not a symmetric dampening: it costs you nothing to move cautiously, and it caps your reward for moving too aggressively, in whichever direction "too aggressively" would be a problem.

**Step 4 — why this substitutes for an explicit KL term.** Because the clip bounds are placed directly on the ratio $r_t = \pi_\theta/\pi_{\text{old}}$, and this ratio is itself the same quantity a first-order KL-divergence approximation would bound, PPO's clip achieves a similar qualitative effect (bounded per-step policy movement) to TRPO's explicit KL constraint, at the cost of only a comparison-and-clip operation per action rather than a constrained optimization solve — the entire computational saving comes from approximating a global divergence constraint with a simple, local, per-action bound.

## Practical pattern

1. treat $\epsilon$ (the clip range) as the primary stability-versus-speed dial in a PPO implementation — smaller $\epsilon$ trades training speed for extra stability margin, larger $\epsilon$ trades stability margin for faster convergence when the advantage estimates are trustworthy;
2. verify your implementation's $\min(\cdot,\cdot)$ logic against both advantage signs explicitly (as derived above) — a common implementation bug applies the clip symmetrically without accounting for how the sign of $A_t$ changes which side of the clip bound is actually binding;
3. prefer PPO over exact TRPO whenever you need to train at a scale where per-update conjugate-gradient solves would be prohibitively expensive — which, in practice, is essentially every modern large-language-model RLHF setting;
4. remember that PPO's stability guarantee is weaker and more heuristic than TRPO's — it approximates the effect of a trust region rather than proving one, so pathological cases (very large, poorly-estimated advantages) can still occasionally destabilize training and warrant monitoring.

## Common traps

- implementing the clip symmetrically without accounting for how the sign of the advantage flips which clip bound actually binds — get this wrong and the "tiny feet" guarantee silently stops holding for negative-advantage actions;
- treating $\epsilon$ as a universal default rather than a problem-specific hyperparameter — the right value depends on advantage-estimate noise and reward scale, both of which vary by task;
- assuming PPO provides the same theoretical monotonic-improvement guarantee as exact TRPO — PPO is a fast, effective heuristic approximation, not a drop-in mathematical equivalent;
- forgetting that PPO's clip only limits *how much this update can move the ratio*, not the total distance the policy can drift over many updates — long training runs still need separate anchoring (a KL term against a fixed reference model) if long-run drift is a concern, exactly the technique the next page's DeepSeek discussion revisits.

## Takeaways

- PPO replaces TRPO's expensive, exact KL-divergence trust region with a cheap clip on the probability ratio $r_t(\theta) = \pi_\theta/\pi_{\text{old}}$, bounded to $[1-\epsilon, 1+\epsilon]$.
- The clipped objective's $\min(\cdot,\cdot)$ structure is a deliberate, provable pessimism: it removes the incentive for excessive per-step movement without ever granting extra credit for having moved too far.
- This simplification is precisely why PPO, not TRPO, was practical enough to become the algorithm that trained ChatGPT's RLHF stage at real production scale.
- PPO's stability guarantee is heuristic, not exact — very large or poorly-estimated advantages can still occasionally destabilize training, and long-run drift across many updates still benefits from an explicit anchor to a reference policy.
