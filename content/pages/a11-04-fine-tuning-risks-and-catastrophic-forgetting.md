---
id: a11-04-fine-tuning-risks-and-catastrophic-forgetting
title: "The Sand Analogy: Why Fine-Tuning Can Break What It Doesn't Touch"
week: 11
topic: "Act II: The Risks Beneath the Escalation Ladder"
order: 4
summary: Fine-tuning nudges a probability distribution rather than replacing it, and pushed too hard it borrows probability mass from abilities you never meant to touch — producing catastrophic forgetting and mode collapse that show up in surprising, specific ways.
course: ai_agents
---

A model fine-tuned on corporate Slack messages absorbed something its trainers never intended: the corporate *dharma* of deferring tasks. Where it should have answered a question directly, it started politely promising to "get back to you tomorrow" — because that behavior was statistically dominant in its training data, and the fine-tuning process, doing exactly what it was told to do, generalized it. This is not a bug in the ordinary sense. It is the predictable consequence of what fine-tuning actually is: not surgical instruction of one narrow skill, but a reshaping of an entire probability distribution, with side effects that are only obvious in hindsight.

This page works through the mechanics of that risk — using the course's own sand-pile and brain-surgery analogies — because the earlier weeks' escalation ladder treats fine-tuning as a rung you climb *to*, and this page is the necessary caution about what you can lose on the way up.

## Core intuition

Think of a model's learned behavior as a probability distribution — a pile of sand spread across every possible response. Fine-tuning on new, domain-specific data means the new data has a slightly different distribution than what the model originally learned, and reshaping the pile to raise probability in some places requires **borrowing sand from somewhere else**. If this is done carefully, the borrowed sand comes from irrelevant, low-value places. If it is done too aggressively — too much gradient descent, too many epochs, too much data — the model may effectively conclude its *entire* prior distribution was wrong and discard it, rather than nudging toward the new one. This is **catastrophic forgetting**: a systemic, widespread loss of prior abilities. It often surfaces partially, as **mode collapse**, where specific abilities vanish while others remain intact.

## Why it matters

Mode collapse is not a hypothetical risk — it shows up in specific, documented, sometimes bizarre ways. Fine-tuning on math and coding data that is disproportionately drawn from Mandarin- and Indian-language technical communities can cause a model to lose the ability to stay in one language even when explicitly asked to answer in English, mixing in Mandarin or other languages mid-response — a multilingual mode collapse borrowed directly from the statistical composition of the fine-tuning data, not from any explicit instruction to behave that way. Even outside of deliberate fine-tuning, the same mechanism has been observed informally in production systems adapting their outputs seasonally — ChatGPT reportedly producing shorter, less thorough answers as the December holidays approached, apparently mirroring holiday-season patterns latent in recent interaction data, then reverting once the new year began.

## Instructor framing

Pair this page directly with the earlier escalation-ladder page: that page told you *when* to climb to fine-tuning; this page tells you what the climb costs even when it succeeds. The brain-surgery analogy below is worth returning to any time a later page (on RLHF, DPO, or GRPO) describes a training run as producing a clear capability gain — ask, in the same breath, what capability that run most likely borrowed against, and whether your specific application can afford the loss.

## Worked example

Fine-tuning is best understood through the **brain surgery analogy**: every act of brain surgery is irreversible. If a surgeon must remove a tumor, they enter the brain along some path, and along that path, some functionality is necessarily lost — nerves are cut, tissue is disturbed. The hope is that the lost functionality is redundantly covered by another part of the brain, but the surgeon cannot pretend nothing was sacrificed. In model fine-tuning, adding a capability follows the same logic: you must assume something else was degraded, and the actual engineering question is never "did we gain the new skill" but "was the specific thing we lost irrelevant to our real-world use case."

Contrast this with pre-training's Chinchilla-optimal regime, where "more data is better" is close to a law. Fine-tuning inverts that intuition entirely: **less is better**. More fine-tuning data, or more epochs over it, increases the risk of catastrophic forgetting and mode collapse rather than reliably improving the target skill — which is precisely why fine-tuning is described in the course as a nuanced, dangerous art, closer to learning the violin (a beginner's early attempts are actively unbearable, not merely mediocre) than to a mechanical, always-safe procedure.

## Math explained step by step

Model the sand-pile intuition as a constrained reallocation of a fixed probability budget, to see exactly why "more fine-tuning" is not free.

**Step 1 — probability mass is conserved.** For any input, the model's output distribution over all possible responses sums to 1: $\sum_i P(y_i \mid x) = 1$. Raising $P(y_j \mid x)$ for a target response $y_j$ during fine-tuning necessarily lowers $\sum_{i \ne j} P(y_i \mid x)$ by the identical amount — there is no way to add probability mass to one region without removing it from others.

**Step 2 — the fine-tuning gradient doesn't know which "elsewhere" is safe to take from.** A standard SFT loss gradient $\nabla_\theta \mathcal{L}$ pushes $\theta$ toward higher $P(y_j \mid x)$ on the fine-tuning examples, but has no explicit term protecting any *specific* pretrained capability — whichever capability's probability mass is geometrically "nearest" to the direction of steepest descent gets reduced first, and that capability is not chosen by the engineer; it falls out of the model's existing geometry.

**Step 3 — quantify aggressiveness via step size and epoch count.** The total distributional shift after $E$ epochs at learning rate $\eta$ scales roughly with $E \cdot \eta$ (more precisely, with the cumulative norm of applied gradient updates). Small $E \cdot \eta$ produces a small, localized reallocation — sand moved from nearby, low-value bowls. Large $E \cdot \eta$ risks a global reallocation — sand moved from anywhere, including bowls representing capabilities entirely unrelated to the fine-tuning task, which is the mechanistic description of catastrophic forgetting.

**Step 4 — the practical design rule this implies.** Because the risk scales with cumulative update magnitude rather than with any measure of "how much new skill was gained," the correct mitigation is not "train until the target metric looks good" but "train with the smallest $E \cdot \eta$ that achieves an acceptable target metric" — checking held-out performance on *unrelated* prior capabilities as a first-class stopping criterion, not merely checking performance on the fine-tuning task itself.

## Practical pattern

1. before fine-tuning, identify a held-out evaluation suite covering capabilities *unrelated* to the fine-tuning target, and monitor it throughout training as a forgetting canary — a rising target-task score alongside a falling canary score is the sand-pile trade-off made visible;
2. default to the smallest amount of fine-tuning data and the fewest epochs that achieve your target metric, rather than assuming more data or more epochs is strictly better — this inverts the pre-training intuition deliberately;
3. audit your fine-tuning data's demographic and linguistic composition before training, since mode collapse (like the multilingual example) often traces directly back to statistical skew in the data rather than any explicit behavioral instruction;
4. treat LoRA and other lower-rank, more contained fine-tuning techniques as a first choice for reducing the "surface area" of what can be perturbed, reserving full-model fine-tuning for cases where the constrained approach measurably underperforms.

## Common traps

- treating fine-tuning as strictly additive — assuming a new capability can only be gained, never accompanied by a loss elsewhere in the model's behavior;
- evaluating a fine-tuning run only against its target task's metric, missing degradation on unrelated capabilities that a broader eval suite would have caught immediately;
- assuming "more fine-tuning data is better," carried over uncritically from pre-training intuition, when the opposite is closer to true for the fine-tuning regime;
- fine-tuning on data with unexamined demographic, linguistic, or stylistic skew and being surprised when the resulting model absorbs that skew as an unintended behavior change.

## Takeaways

- Fine-tuning reshapes a fixed probability budget rather than adding capability for free — every gain in the target skill borrows probability mass from somewhere else in the model's distribution.
- Catastrophic forgetting and its partial form, mode collapse, are the visible symptoms of pushing that reallocation too far, and have been observed in concrete forms: language mixing, behavioral shifts absorbed from training data, even apparent seasonal drift.
- Unlike pre-training, where more data reliably helps, fine-tuning inverts the intuition — less data and fewer epochs reduce the risk of catastrophic forgetting, making restraint a deliberate design choice rather than a shortcut.
- Always evaluate a fine-tuning run against a held-out suite of *unrelated* capabilities, not just the target task, since the target metric alone cannot reveal what was quietly lost along the way.
