---
id: a8-06-deepseek-pipeline-enterprise-practice
title: "From SaaS to DeepSeek: How Fine-Tuning Actually Gets Shipped"
week: 8
topic: "Act II: Surgical Fine-Tuning — From Full Updates to LoRA"
order: 6
summary: Practical fine-tuning splits into SaaS platforms and code-based approaches, base vs. instruct models present a real starting-point trade-off, and DeepSeek's published pipeline shows mode collapse being deliberately induced and then deliberately repaired within one training run.
course: ai_agents
---

Everything covered so far in this fine-tuning unit — the theory of representation learning, the LoRA math, the constrained-optimization framing — eventually has to become a running training job that produces an actual, shippable model. This page is about that last mile: the practical choices (SaaS versus code, base versus instruct model, LoRA versus full fine-tuning) that determine how a real team actually executes on the theory, and a genuinely surprising real-world case study — DeepSeek's published training pipeline — that shows mode collapse being deliberately triggered and then deliberately reversed, on purpose, within a single production training process.

The DeepSeek case is worth taking seriously specifically because it inverts the previous pages' framing of forgetting as purely a risk to be minimized — here it's a risk that gets used as a tool, with a planned recovery step built directly into the pipeline.

## Core intuition

Two practical tracks exist for actually doing fine-tuning. The **SaaS approach** (platforms like Fireworks.ai or Unsloth) lets a user fine-tune through a simple UI — select a base model, upload a labeled dataset (commonly Q&A pairs), set hyperparameters (epochs, batch size, learning rate, and rank if using LoRA) — trading some control for a fast, low-friction path to a working fine-tuned model. The **code approach** uses libraries directly (Hugging Face's `transformers` `Trainer` class for full fine-tuning, the `peft` library's `LoraConfig` and `PeftModel` for LoRA), trading implementation effort for full control over the process.

A separate, orthogonal decision is **base versus instruct model** as your starting point. A base model has undergone only pre-training on raw, web-scale data — maximally flexible, but with no built-in guardrails or instruction-following alignment, meaning you must build all safety and behavioral discipline yourself. An instruct model has additionally undergone Supervised Fine-Tuning and Reinforcement Learning to align it with human instructions and safety guardrails — a head start on discipline and safety, often preferable specifically for domain adaptation where you want to inherit that existing alignment rather than rebuild it from scratch.

## Why it matters

The DeepSeek pipeline is the concrete case study that ties the previous pages' abstract "mode collapse is a risk to manage" framing into something more nuanced: DeepSeek's published process reportedly reduced the human-labeling-intensive Supervised Fine-Tuning phase by 80-90% by starting from a base model, fine-tuning on a *small* set of Chain-of-Thought examples (thousands, not millions), and then applying GRPO — a rule-based reward model — to strengthen reasoning through reinforcement learning rather than exhaustive human-labeled supervision.

This aggressive reasoning-focused training reportedly caused genuine mode collapse — the model lost general capabilities as a side effect of being pushed hard toward strong reasoning performance, exactly the risk earlier pages warned about. But DeepSeek's pipeline treats this not as an unplanned accident to be avoided at all costs, but as an anticipated, managed trade-off with a built-in fix: fine-tune again on a non-reasoning dataset (general writing, general QA) specifically to restore the generalization that was lost, then apply GRPO a second time. The result, per the published pipeline, is a highly capable reasoning model achieved with dramatically less human-labeled data than the traditional SFT-heavy approach requires — a genuinely different way of relating to catastrophic forgetting than "prevent it at all costs."

## Instructor framing

Present the DeepSeek case as a controlled, deliberate exception to the earlier pages' "minimize forgetting" framing, not a contradiction of it — the distinction that makes this work is that DeepSeek's team *anticipated* the specific mode collapse their aggressive reasoning-focused training would cause, and *planned* a specific corrective step (the non-reasoning restoration fine-tune) to address exactly that anticipated damage, rather than accepting undirected, unmonitored forgetting as an acceptable cost. Students should come away understanding that the constrained-optimization framing from earlier pages isn't violated here — it's satisfied via a two-stage process (deliberately incur forgetting for a specific gain, then deliberately repair it) rather than the single-stage "avoid forgetting throughout" process those pages implicitly assumed.

## Worked example

A team choosing between the SaaS and code approaches for a first fine-tuning project sizes up their actual needs: if the goal is a straightforward domain-adaptation fine-tune with a modest labeled dataset and no unusual architectural requirements, a SaaS platform's simple UI — select base model, upload Q&A pairs, set epochs and learning rate — gets to a working result fastest, with the trade-off that they're accepting the platform's implicit choices about which layers get adapted and how. If the project needs fine-grained control — say, implementing a custom reward signal for reinforcement learning, or precisely controlling which layers a LoRA adapter attaches to based on a gradient-heatmap analysis from an earlier page — the code approach via Hugging Face's `Trainer` and the `peft` library is the right investment of effort, since the SaaS platform's abstraction would hide exactly the control the project needs.

On base versus instruct: a team building a legal-domain assistant chooses to start from an *instruct* model specifically because they want the model's existing safety alignment and instruction-following discipline to carry over into the legal domain, and don't want to rebuild those properties from scratch on top of a base model — domain adaptation is their actual goal, not building a new alignment layer. A research team building an experimental agent architecture that needs unusual, non-standard behavior patterns instead starts from a *base* model, deliberately accepting the burden of building their own guardrails, because the instruct model's existing alignment might actually conflict with or constrain the unusual behavior they're trying to elicit.

## Math explained step by step

Quantify the labeling-cost reduction DeepSeek's pipeline claims, since "80-90% reduction" deserves the underlying mechanism, not just the headline number.

**Step 1 — traditional SFT labeling cost.** A traditional instruct-model pipeline requires a large volume of human-labeled instruction-following examples, $N_{\text{traditional}}$, to align a base model — a cost that scales with the breadth and quality of alignment desired, and is human-labor-intensive (expensive and slow) by nature.

**Step 2 — DeepSeek's substitution.** DeepSeek's pipeline instead uses a small set of Chain-of-Thought examples, $N_{\text{deepseek}} \ll N_{\text{traditional}}$ (thousands rather than the much larger volumes traditional SFT relies on), followed by GRPO — a *rule-based* reward model, meaning the reward signal is computed algorithmically rather than requiring human labelers to score each output. This substitution replaces a large fraction of what would have been human-labeling cost with automated, rule-based reward computation.

**Step 3 — express the reduction.** If traditional SFT requires labeling cost proportional to $N_{\text{traditional}}$, and DeepSeek's approach requires labeling cost proportional to $N_{\text{deepseek}}$ plus the (much cheaper, automatable) cost of running GRPO's rule-based rewards, the reported 80-90% reduction corresponds to $N_{\text{deepseek}} / N_{\text{traditional}} \approx 0.1\text{-}0.2$ — roughly a fifth to a tenth of the original human-labeling volume, with the remaining capability gain coming from reinforcement learning against automated rewards rather than additional human supervision.

**Step 4 — the two-GRPO-pass structure as risk-managed sequencing.** The pipeline's two-pass structure — GRPO (aggressive reasoning gain, incurring mode collapse) → restoration fine-tune on non-reasoning data (repair the specific damage) → GRPO again (recover reasoning gains on the now-restored, more general model) — is a sequencing decision that lets the pipeline capture the compute-efficient reasoning gains from aggressive reinforcement learning while still ending at a broadly capable model, rather than needing to choose upfront between "aggressive reasoning training" and "broad general capability" as mutually exclusive alternatives.

## Practical pattern

Applying these practical decisions to a real fine-tuning project:

1. choose SaaS versus code based on how much control your specific project actually needs — default to SaaS for standard domain-adaptation or task-specificity fine-tunes with conventional requirements, and reserve the code approach for projects needing custom reward signals, precise layer targeting, or architectural experimentation the SaaS abstraction would obscure;
2. choose base versus instruct deliberately: start from instruct when you want to inherit existing alignment and safety discipline (most domain-adaptation projects), and start from base only when you have a specific reason the instruct model's existing alignment might conflict with or constrain your target behavior;
3. if your project's fine-tuning strategy involves any deliberately aggressive training phase likely to induce forgetting (analogous to DeepSeek's reasoning-focused GRPO pass), plan the corrective restoration phase *in advance*, as part of the pipeline design, rather than treating forgetting purely as an unplanned risk to be monitored for and reacted to after the fact;
4. invest in robust MLOps infrastructure — checkpointing, multi-GPU orchestration, monitoring — before running any long training job; the course's cautionary example of a 7-hour fine-tuning job failing overnight with the work lost is a reminder that the actual bottleneck in enterprise fine-tuning is very often the pipeline's reliability, not the model theory.

## Common traps

- choosing the code approach purely for the sense of control it provides, when a SaaS platform would deliver a comparable result faster for a standard fine-tuning need that doesn't actually require the extra flexibility;
- choosing a base model as the starting point without accounting for the alignment and guardrail-building burden this creates, and then being surprised the resulting model lacks the instruction-following discipline an instruct model would have provided for free;
- attempting a DeepSeek-style aggressive-training-then-repair strategy without planning the repair phase in advance, effectively taking on the forgetting risk from the aggressive phase without the specific mitigation that makes the strategy work as a coherent pipeline rather than an unmanaged gamble;
- underinvesting in MLOps reliability (checkpointing, restart-from-failure capability) relative to time spent on model-theory refinement, when in practice the pipeline's operational robustness is often the more common point of failure in real projects.

## Takeaways

- Practical fine-tuning execution splits along two largely independent axes: SaaS versus code (how much implementation control you need) and base versus instruct model (whether you want to inherit existing alignment or build your own from scratch) — and the right choice on each axis depends on the specific project's requirements, not a universal default.
- DeepSeek's published pipeline substitutes a small Chain-of-Thought fine-tune plus rule-based GRPO reinforcement learning for the much larger human-labeling volume traditional Supervised Fine-Tuning requires, reportedly cutting labeling cost by 80-90%.
- DeepSeek's two-pass GRPO structure — deliberately induce mode collapse during an aggressive reasoning-focused phase, then deliberately repair it with a restoration fine-tune before a second GRPO pass — shows that catastrophic forgetting can be a planned, managed trade-off rather than purely a risk to avoid, provided the corrective step is designed into the pipeline in advance.
