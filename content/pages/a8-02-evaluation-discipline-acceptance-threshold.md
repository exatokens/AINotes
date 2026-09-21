---
id: a8-02-evaluation-discipline-acceptance-threshold
title: "Knowing When to Stop: The Acceptance Threshold"
week: 8
topic: "Act I: The Anatomy and Risk of Fine-Tuning"
order: 2
summary: Fine-tuning needs a metric, a realistic evaluation dataset, and an agreed acceptance threshold defined before training starts — because fine-tuning is a constrained optimization problem where "more training" is not automatically better.
course: ai_agents
---

There's a specific kind of mistake that happens when a team starts fine-tuning without first agreeing on what "done" looks like: they keep training because performance keeps improving on whatever they're watching, and stop only when time or budget runs out, not when the model actually meets the bar the business needs. This isn't a minor process gap — it's the single biggest reason fine-tuning projects either under-deliver (stopped too early, against no defined bar) or overshoot into real risk (kept training past the point where returns diminished and damage started accumulating).

The fix is a discipline the course lays out in three concrete steps, established *before* any training begins, not improvised once results start coming in. This page is about why that ordering matters and what each step actually has to accomplish.

## Core intuition

Establish, before training starts: **metrics** — a ruler to measure success, chosen to match the task (precision@k or AUC for a search task, accuracy or F1 for classification); an **evaluation dataset** — built to genuinely reflect the real-world problem the model will face in production, not a convenient or easy proxy; and an **acceptance threshold**, $\tau_{\text{threshold}}$ — the minimum performance level that business stakeholders and engineers agree, in advance, constitutes success. Fine-tuning is only necessary at all if current performance $\tau$ is substantially below this threshold, and training should stop once $\tau$ exceeds $\tau_{\text{threshold}}$ — not before, and importantly, not indefinitely after either.

## Why it matters

This ordering — metric, then evaluation set, then threshold, all fixed before training — matters because each piece constrains the ones that follow it and prevents a specific kind of self-deception. Choosing the metric after seeing results risks cherry-picking whichever number happens to look best. Building the evaluation dataset from data the model has effectively already seen risks an inflated performance estimate that won't hold in production. And deciding the acceptance threshold only after training is underway risks moving the goalposts to match whatever the model happens to achieve, rather than what the business actually needs — turning a rigorous stopping criterion into a post-hoc rationalization.

The radio-dial analogy captures why stopping matters as much as starting: a pre-trained foundational model is like an old-style radio where the manufacturer has already set the large dial to roughly the right station — the general vicinity is right, but there's static. Fine-tuning is the small, precise dial that removes the static and gets a crisp signal. Crucially, that small dial has a point of diminishing and then *negative* returns: past the point of a clear signal, continuing to turn the fine dial doesn't produce an even clearer signal — it starts tuning past the station entirely into static again. The acceptance threshold is what tells you the signal is already clear enough to stop turning.

## Instructor framing

Teach this as a pre-registration discipline, borrowing directly from the same logic that makes pre-registered experiments trustworthy in empirical science: decide the metric, the evaluation criteria, and the success bar before you have any results that could bias those decisions. Ask students to imagine the alternative — announcing "we'll know success when we see it" — and have them articulate concretely what goes wrong (cherry-picked metrics, an evaluation set quietly drifting toward whatever the model is already good at, a threshold retroactively set to match whatever number training happened to produce). This exercise in imagining the failure mode is more durable than simply stating the rule.

## Worked example

A team fine-tuning a customer-support classification model to route tickets to the right department defines its evaluation discipline before touching any training code: the metric is F1 score across department categories (chosen over raw accuracy because department volume is imbalanced, and F1 better reflects performance on smaller, less common categories that accuracy alone would let the model neglect). The evaluation dataset is built from a held-out sample of *actual* historical tickets spanning a full year, deliberately including seasonal variation and edge cases the team has seen cause routing mistakes in the past — not a convenient synthetic dataset that looks clean but doesn't reflect production messiness. The acceptance threshold, $\tau_{\text{threshold}} = 0.85$ F1, is agreed between the engineering team and the support-operations stakeholders who will actually depend on the system, based on what routing accuracy would meaningfully reduce their current manual-triage burden.

Training proceeds, and F1 crosses 0.85 at epoch 6. Following the pre-registered discipline, the team stops there — not because they've run out of budget, but because the pre-agreed bar for success has been met, and continued training risks the radio-dial's negative-returns territory: overfitting to the specific evaluation set's quirks, or catastrophic forgetting of general capability the model needs to gracefully handle genuinely novel ticket types it wasn't specifically trained on.

## Math explained step by step

Formalize the stopping rule and why continuing training past $\tau_{\text{threshold}}$ carries real, quantifiable risk rather than simply being "extra effort with no downside."

**Step 1 — state the stopping rule precisely.** Training should continue only while $\tau < \tau_{\text{threshold}}$, where $\tau$ is measured on the pre-defined held-out evaluation set using the pre-defined metric. The rule is not "train until performance stops improving" — it's "train until the agreed bar is met," which are different stopping conditions whenever performance could plausibly keep improving (on the evaluation metric, or worse, on the training set alone) past the point where it actually matters for the business need.

**Step 2 — model overfitting risk as a function of continued training beyond the threshold.** Let $\Delta$ be the amount of additional training performed after $\tau$ first exceeds $\tau_{\text{threshold}}$. Held-out generalization performance typically follows a curve that improves with training up to a point and then plateaus or declines as the model increasingly fits idiosyncrasies of the training set rather than the underlying pattern — so risk of degraded true (not just measured) performance is monotonically non-decreasing in $\Delta$ once $\tau_{\text{threshold}}$ has already been cleared, even though the number being watched during training might still appear to be improving.

**Step 3 — connect to catastrophic forgetting explicitly.** Continued training beyond the point needed to hit $\tau_{\text{threshold}}$ also increases the risk of catastrophic forgetting — general capabilities the model had before fine-tuning began eroding as an unintended side effect of further parameter updates optimized narrowly for the fine-tuning objective. This risk compounds the overfitting risk from step 2: both are forms of "the model is now optimized more narrowly than it needs to be for the actual business requirement," and both grow with unnecessary additional training.

**Step 4 — the correct trade-off given both risks.** Since neither generalization performance nor general-capability retention improves monotonically with training time past $\tau_{\text{threshold}}$, and both can *degrade* with continued training, the mathematically correct stopping point is the earliest point at which $\tau \geq \tau_{\text{threshold}}$ is first satisfied — not the point of maximum observed performance on whatever metric is being watched live during training, which may already reflect the beginning of overfitting rather than genuine improvement.

## Practical pattern

Establishing and following an evaluation discipline for a real fine-tuning project:

1. select the metric before writing any training code, and choose it to match the task's actual shape (ranking-style metrics like precision@k or AUC for retrieval/search tasks, F1 or accuracy for classification, task-appropriate metrics for generation) rather than defaulting to whatever's easiest to compute;
2. build the evaluation dataset from data that genuinely represents production conditions — including known edge cases, class imbalance, and seasonal or temporal variation — and keep it strictly held out from any training data to avoid an inflated, non-generalizing performance estimate;
3. negotiate and document the acceptance threshold with the actual business stakeholders who will depend on the system, before training begins, so the number reflects a genuine operational requirement rather than being set retroactively to match whatever training happens to achieve;
4. stop training at the first point $\tau \geq \tau_{\text{threshold}}$ is met on the held-out evaluation set, resisting the temptation to keep training "for a bit more improvement," given that both overfitting risk and catastrophic-forgetting risk grow, not shrink, with unnecessary continued training past that point.

## Common traps

- choosing a metric after seeing early results, effectively cherry-picking whichever number makes the model look best rather than the one that actually reflects the business need;
- building or curating an evaluation dataset that's easier or cleaner than real production data, producing an inflated performance estimate that won't hold once the model faces genuine production messiness;
- setting the acceptance threshold only after training results are visible, turning a discipline meant to prevent goalpost-moving into a mechanism for retroactively justifying whatever was achieved;
- continuing to train past the point where $\tau_{\text{threshold}}$ is first met, in pursuit of a higher number on the live-monitored metric, without recognizing that continued training carries real overfitting and catastrophic-forgetting risk that isn't offset by marginal gains on an already-sufficient metric.

## Takeaways

- A rigorous fine-tuning process fixes three things before training starts: the metric, a realistic held-out evaluation dataset, and an agreed acceptance threshold $\tau_{\text{threshold}}$ — deciding any of these after seeing results undermines the discipline's whole purpose.
- The radio-dial analogy captures why "more training" is not automatically better: past the point of a clear signal, further fine-tuning can tune past the target into static, both through overfitting to evaluation-set idiosyncrasies and through catastrophic forgetting of general capability.
- The correct stopping rule is the earliest point $\tau \geq \tau_{\text{threshold}}$ is satisfied on the held-out evaluation set — not the point of maximum observed performance during training, since continued training past a sufficient threshold carries real, growing risk with no corresponding business benefit.
