---
id: a3-03-prompting-toolkit-zero-few-shot-cot
title: "Zero-Shot, Few-Shot, and Why Chain-of-Thought Became a Bad Idea"
week: 3
topic: "Act II: The Prompting Toolkit"
order: 3
summary: Zero-shot and few-shot prompting remain broadly useful, but chain-of-thought prompting — once essential before genuine reasoning models existed — is now counterproductive for reasoning models, because it shackles a model that has figured out a better way to think.
course: ai_agents
---

The prompting techniques catalogued this week aren't presented as a menu of equally good options to mix and match freely. They're presented with a historical arc, and the arc matters, because the single most surprising claim in this week's material is that one of the most famous prompting techniques of the last several years — chain-of-thought — has gone from essential to actively harmful, and the reason is directly tied to the same breakthrough (RL-induced genuine reasoning) that this bootcamp keeps returning to.

Understanding *why* a technique flipped from good to bad is more valuable than memorizing the current list, because it tells you how to reason about whichever technique gets invented next.

## Core intuition

Zero-shot prompting asks a model to perform a task with no examples at all, relying on it to infer the intended task from context — and it works surprisingly often, because a well-trained model can pick up on cues like "classify this text into neutral, negative, and positive" without needing the word "sentiment" spelled out. Few-shot prompting supplies a small number of examples, using clear formatting markers, to pin down the desired output format and logic more precisely. Chain-of-thought prompting supplied worked, step-by-step reasoning *examples*, so a model could imitate that reasoning pattern on a new problem — genuinely necessary before models could reason natively, and actively counterproductive now that many can, because a demonstrated reasoning path can shackle a genuinely capable model into a simpler, worse strategy than the one it would discover on its own.

## Why it matters

Getting this history wrong has a specific, silent cost: applying chain-of-thought prompting to a modern reasoning model doesn't just fail to help — it can measurably hurt, by forcing the model to follow the shape of your example's reasoning even when it "would have figured out deeper ways to think" left unconstrained. This week's material states the conclusion bluntly: "chain of thought is a very bad idea" in prompts written for reasoning models. That's a strong claim, and it's worth taking seriously rather than treating chain-of-thought as a universally safe technique to reach for by habit.

## Instructor framing

Have students trace exactly *why* the flip happened, not just accept that it happened. Before genuine reasoning capability existed, an LLM predicting a final answer directly was doing something closer to pattern completion — chain-of-thought examples gave it a demonstrated intermediate procedure to imitate, converting a hard, single-step prediction into an easier, guided multi-step one. Once a model can genuinely search over its own reasoning strategies internally (the RL-induced capability from earlier weeks), supplying a fixed worked example no longer helps it search better — it constrains the search to match your example's specific path, which may not be the best path for this particular instance of the problem.

## Worked example

Take a multi-step word problem: "A store had 120 items, sold 35% on Monday and 20% of the remainder on Tuesday, how many are left?" For an early, non-reasoning model, a chain-of-thought example showing "first compute 35% of 120, then subtract, then compute 20% of the remainder, then subtract again" was often the difference between a correct and incorrect answer — the model had no internal mechanism to decompose the problem itself, so the demonstrated decomposition did that work for it. For a modern reasoning model, handing it that same worked example risks a subtler failure: if the *actual* problem in front of it has a slightly different structure — say, a discount that applies before rather than after a different discount — a model shackled to imitate the demonstrated step order may misapply that structure to the new problem's different arithmetic, where a model left free to reason about this specific problem's structure would have decomposed it correctly on its own. The modern, recommended use of chain-of-thought this week describes is inverted from its original purpose: use it as an *evaluative* tool, reading back a reasoning model's own generated reasoning trace to check its logical consistency after the fact, rather than as a *guidance* tool supplied before generation.

## Math explained step by step

The shackling effect has a clean way to state formally, using the same latent-strategy framing introduced for role-prompting in Week 2.

**Step 1 — model a reasoning model's unconstrained strategy search.** Left unconstrained, a genuinely reasoning-capable model implicitly searches over a space of candidate solution strategies $\{\sigma_1, \sigma_2, \ldots\}$ and selects (or synthesizes on the fly) whichever strategy $\sigma^*$ best fits the specific problem instance in front of it, with expected quality $Q(\sigma^* \mid \text{problem})$.

**Step 2 — model what a chain-of-thought example does to this search.** Supplying a worked example demonstrating strategy $\sigma_{\text{demo}}$ conditions the model's generation heavily toward imitating $\sigma_{\text{demo}}$'s shape, effectively restricting the search to a small neighborhood around $\sigma_{\text{demo}}$ rather than the full space $\{\sigma_1, \sigma_2, \ldots\}$.

**Step 3 — see when this restriction helps versus hurts.** If $\sigma_{\text{demo}}$ happens to be close to $\sigma^*$ for the actual problem at hand, the restriction is harmless or even mildly helpful (faster convergence to a good answer). If the actual problem's ideal strategy $\sigma^*$ differs meaningfully in structure from $\sigma_{\text{demo}}$ — which becomes increasingly likely as problem diversity increases — the restriction actively lowers achievable quality: $Q(\sigma_{\text{demo}}\text{-shaped output}) < Q(\sigma^*)$, and the gap is exactly the cost of shackling.

**Step 4 — see why non-reasoning models don't face this trade-off the same way.** For a model with no strong internal search over $\{\sigma_1, \sigma_2, \ldots\}$ at all, there is no $\sigma^*$ being displaced — the choice is between $\sigma_{\text{demo}}$-guided generation and no coherent strategy at all, so the demonstrated example is close to pure upside. This is precisely the axiom-2-versus-modern-models distinction the source material draws: chain-of-thought's value is contingent on whether the model has an internal search worth *not* overriding.

## Practical pattern

1. Default to zero-shot prompting first for any task, especially with a modern reasoning model — it's the cheapest to write and lets the model's own strategy search operate unconstrained.
2. Use few-shot examples specifically to pin down output *format* and demarcation conventions (clear separators like `//`, consistent structure) rather than to demonstrate a reasoning *procedure* — format specification doesn't compete with the model's internal strategy search the way procedural demonstration does.
3. Reserve chain-of-thought-style worked examples for models you know or suspect lack strong native reasoning, or for narrowly-scoped tasks where you specifically want to enforce one particular procedure regardless of whether the model would have found a better one.
4. Use chain-of-thought in the *opposite* direction with modern reasoning models: read the model's own generated reasoning trace back, and evaluate it for logical consistency, rather than feeding it a demonstrated trace beforehand.

## Common traps

- Reflexively adding worked chain-of-thought examples to every prompt out of habit, without checking whether the target model has native reasoning capability that the example might actually constrain.
- Assuming more detailed, more thoroughly worked examples are always better — for a genuinely reasoning-capable model, a highly specific worked example can narrow its strategy search more aggressively, increasing the risk of shackling on structurally different problem instances.
- Confusing few-shot examples meant to specify output format with chain-of-thought examples meant to demonstrate a reasoning procedure — they serve different purposes and carry different risks.
- Failing to distinguish, when debugging a failed prompt, whether the failure came from insufficient guidance (fixable with better examples) or over-constraining guidance (fixable by removing the chain-of-thought example entirely).

## Takeaways

- Zero-shot and few-shot prompting remain broadly useful; chain-of-thought prompting has inverted from essential to often counterproductive as models gained native reasoning capability.
- The mechanism is a strategy-search restriction: a demonstrated reasoning path concentrates a reasoning model's generation around that path's shape, which helps when the demonstrated strategy matches the actual problem and hurts when it doesn't.
- The modern, recommended use of chain-of-thought is evaluative — reading back a model's own reasoning trace to check consistency — rather than instructive.
- Whether a given prompting technique helps or hurts is contingent on the specific model's underlying capabilities, not a fixed, permanent property of the technique itself.
