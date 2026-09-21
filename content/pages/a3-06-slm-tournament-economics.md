---
id: a3-06-slm-tournament-economics
title: "The Model Tournament: Choosing SLMs with Data, Not Opinion"
week: 3
topic: "Act III: Economics and Engineering Discipline"
order: 6
summary: Rather than debating model choice opinion by opinion, run a systematic tournament — optimize a prompt per candidate model, measure error rates empirically, and let the data pick the winner before fine-tuning it further.
course: ai_agents
---

Model selection is one of those decisions that invites endless, unproductive debate — everyone has a favorite frontier model, a favorite open-source model, a strong opinion formed from one good or bad experience, and none of it is actually evidence about which model performs best on *your* specific task. This week's material proposes cutting that debate off entirely with a specific, repeatable process it calls a tournament: assemble multiple candidate models, optimize each one's prompt independently, measure them head to head on the same gold-standard dataset, and let the resulting numbers — not opinions — pick the winner.

This is a direct, practical application of the axiom of measurement from earlier this week, aimed at a decision (which model should power this agent) that too often gets made without any measurement at all.

## Core intuition

Different models respond differently to the same prompt — a prompt tuned for GPT-4 will not necessarily perform equally well, unmodified, on Llama 3.1 or a smaller open model. A fair comparison between models therefore requires comparing each model's *best achievable* performance, not each model's performance under one shared, unoptimized prompt — which is why the tournament process explicitly re-optimizes the prompt per candidate model before comparing them.

## Why it matters

Skipping the per-model optimization step and comparing models under one shared prompt produces a systematically unfair and misleading result: it measures which model happens to respond best to whatever prompt style the tester defaulted to, not which model is genuinely best suited to the task. This matters economically because it's exactly the decision point where the Week 1 SLM-versus-frontier cost argument becomes actionable — the tournament is how you find out, empirically, whether a smaller, cheaper model can match or beat a frontier model on your specific task, rather than assuming the answer either way.

## Instructor framing

Frame the tournament as directly analogous to a controlled scientific experiment: the "treatment" being tested is the model, and prompt optimization per model is the necessary control that isolates the model's true contribution from confounding prompt-quality differences. Skipping the control (comparing unoptimized, shared prompts across models) is the equivalent of comparing two medications where one patient group also got better sleep and diet — you can't attribute the outcome difference cleanly to the thing you actually wanted to measure.

## Worked example

Suppose a team is deciding which model should power a customer-email classification agent, weighing GPT-5, Claude, Gemini, and two open-source candidates in the 30-70B range intended for local or self-hosted deployment. Following the tournament process: first, assemble the candidates in a local testbed (the material specifically recommends LLM Studio for local development and vLLM for production serving). Second, for each candidate, run dynamic prompt optimization (a tool like DSPy, covered elsewhere this course) against the team's gold-standard dataset to find that specific model's best achievable prompt — this step alone typically changes the ranking relative to a shared, unoptimized prompt, because different model architectures respond to different phrasing and structural cues. Third, run each optimized model-prompt pair against the held-out test set and log error rates, cost per call, and latency into a single comparison table. Fourth, select the winner from the actual numbers — which, following the Week 1 economics argument, might turn out to be one of the smaller open models, since agentic systems built with a well-tuned SLM can plausibly out-perform a single call to a larger frontier model once the iterative agentic loop compensates for the smaller model's raw capacity. Fifth, once a winner is identified, that model becomes the candidate for further fine-tuning, since the same gold-standard dataset used for the tournament is also the training data fine-tuning requires.

## Math explained step by step

The case for running $m$ candidate models through a proper tournament rather than picking one on reputation has a clean expected-value framing.

**Step 1 — define the true best achievable error rate per model.** Let $E_i^*$ be model $i$'s true error rate on the target task, achieved under *its own* best possible prompt (not necessarily known in advance). The tournament's goal is to find $\arg\min_i E_i^*$.

**Step 2 — model what happens without per-model prompt optimization.** Comparing models under one shared, unoptimized prompt $\pi_0$ measures $E_i(\pi_0)$ for each $i$, which can differ substantially from $E_i^*$ — some models are more robust to a suboptimal prompt than others, so $\arg\min_i E_i(\pi_0)$ can easily differ from the true $\arg\min_i E_i^*$, meaning the wrong model gets selected.

**Step 3 — quantify the cost of selecting the wrong model.** If the true best model has error rate $E^*_{\text{best}}$ but the flawed comparison selects a different model with true error rate $E^*_{\text{selected}} > E^*_{\text{best}}$, every future production call pays the difference $E^*_{\text{selected}} - E^*_{\text{best}}$ in extra failures — a permanent, ongoing cost that compounds across the model's entire deployment lifetime, versus the one-time cost of running $m$ separate prompt-optimization passes during the tournament.

**Step 4 — see why the tournament's one-time cost is almost always justified.** The tournament's total cost scales as $O(m)$ prompt-optimization runs, paid once. The cost of selecting the wrong model without it scales as $O(n)$ extra failures across $n$ future production calls, paid forever. For any deployment expected to run at meaningful volume, $n \gg m$ essentially guarantees the one-time tournament investment pays for itself many times over.

## Practical pattern

1. Never compare candidate models under a single shared prompt — always run per-model prompt optimization (manual iteration or a tool like DSPy) before comparing, so the comparison reflects each model's true achievable performance, not its sensitivity to a prompt tuned for a different architecture.
2. Log error rate, cost per call, and latency together in the tournament comparison table — the winning model is not necessarily the one with the lowest error rate alone, especially when a marginally higher error rate comes with a large cost or latency advantage.
3. Use the same gold-standard dataset built for measurement (this week's Act I pages) as the tournament's evaluation set, and the same dataset as the fine-tuning corpus for whichever model wins — this reuses the expensive 90-95%-of-effort dataset-construction work across three purposes.
4. Re-run the tournament periodically as new model versions are released — a model that won last quarter's tournament is not guaranteed to still be the best choice after a competitor's or the same provider's next release.

## Common traps

- Comparing candidate models under a single, shared, unoptimized prompt and concluding the model that happened to respond best to that specific prompt is "the best model" — this measures prompt-robustness, not true task performance.
- Selecting a model based on general reputation or a single team member's prior experience rather than a measured tournament result on the actual task and dataset at hand.
- Treating the tournament as a one-time decision rather than a periodic re-evaluation, missing opportunities as new model versions shift the true ranking.
- Comparing only error rate and ignoring cost and latency, when the actual business decision usually needs to weigh all three together.

## Takeaways

- Model selection should be resolved by a measured tournament — per-model prompt optimization followed by head-to-head evaluation on a shared gold-standard dataset — not by opinion or reputation.
- Skipping per-model prompt optimization before comparison risks selecting the wrong model, since models differ in how sensitive they are to a shared, unoptimized prompt.
- The one-time cost of running a proper tournament is almost always justified by the ongoing cost of selecting a genuinely worse model for a system expected to run at real production volume.
- The same gold-standard dataset serves double duty: it's both the tournament's evaluation set and the eventual fine-tuning corpus for whichever model wins.
