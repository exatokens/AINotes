---
id: a10-06-mapping-reinforcement-learning-onto-llms
title: "Mapping Reinforcement Learning onto Language Models"
week: 10
topic: "Act I: The Vocabulary of Reinforcement Learning"
order: 6
summary: A language model is a reinforcement-learning agent in disguise — the prompt-plus-generated-tokens is the state, the next token is the action, and the whole model is the policy — and this mapping is what makes training LLMs with RL possible at all.
course: ai_agents
---

Every term this week's earlier pages built — agent, environment, state, action, episode, policy, value — was deliberately introduced through Roombas and mice and rabbits, not language models, so that the vocabulary would generalize cleanly. This page cashes in that investment: it maps every one of those terms onto a large language model, term for term, with no metaphor left dangling. Once this mapping clicks, the entire machinery of reinforcement learning — designed originally for robots moving through physical space — becomes available, unmodified in its mathematical core, for training a model that only ever produces text.

This is not an analogy in the loose sense. It is the literal substitution that makes RLHF, PPO, DPO, and GRPO — all covered in the weeks ahead — coherent as *reinforcement learning* algorithms rather than as some bespoke, unrelated technique that happens to also be used for language models.

## Core intuition

The mapping, term by term: the **Agent** is the LLM itself, holding the policy $\pi_\theta$. The **State** ($S_k$) is not a physical location — it is the cumulative context available at a given moment: the original input prompt plus every token generated so far, $x, t_0, \ldots, t_k$. The **Action** ($a_t$) is the generation of the next token — every single word or sub-word the model outputs is one discrete decision made by the policy. The **Policy** ($\pi_\theta$) is the LLM's own probability distribution over the vocabulary, conditioned on the current state: $\pi_\theta(\text{"moon"} \mid \text{"The cow jumped over the ..."})$. The **Trajectory** ($\tau$) is the complete generated response, from first token to end-of-text — the full path taken through the space of possible language. The **Reward** ($R(\tau)$) is a score assigned to the completed response, whether by a human, a reward model, or a verifiable check.

## Why it matters

This mapping resolves a question that otherwise seems paradoxical: how can gradient-based optimization — inherently continuous — ever be applied to something as fundamentally discrete as the choice of a word? The resolution is that RL never tries to differentiate the discrete outcome (which specific token got produced) directly. It differentiates the continuous, smooth *policy* that produces a probability distribution over tokens — exactly the actor from the actor-critic split two pages back, generalized. The agent's "brain," the neural network's parameters $\theta$, is the smooth, adjustable quantity; the emitted token is the discrete, unadjustable consequence. Learning nudges $\theta$ so that high-reward token sequences become more probable, without ever needing to compute a gradient with respect to a token itself.

## Instructor framing

Walk through the mapping slowly and insist students can restate it without looking, because the entire arc of the weeks ahead — from a first RLHF diagram through GRPO's math — assumes this mapping as settled background, not something re-derived each time. If a student is confused later by "why is the state the whole prompt-plus-partial-response and not just the last token," bring them back here: the Markov property this week's vocabulary page insisted on (a state must contain everything the agent needs to act well) is exactly why the LLM's state has to include the *entire* generation history, not just the most recent token — the next word genuinely does depend on everything said before it, not merely on what was just said.

## Worked example

Take the prompt "Tell me a story about a cow on the moon," and suppose the model has already generated "The cow jumped over the ...". At this point in the generation, the **state** is the full string so far — prompt plus partial completion. The **action space** is the entire vocabulary — every possible next token the model could emit. The **policy** assigns a probability to each candidate token conditioned on that state; suppose it assigns high probability to "moon" and low probability to "hammer." Choosing "moon" is the **action**; the environment's "transition rule" is trivial and deterministic here — the new state is simply the old state with "moon" appended. Once the model reaches an end-of-text token, the full generated string, from "The cow" through the final period, is the **trajectory** — and only then does a **reward** get assigned to the whole thing, whether that reward comes from a human labeler's preference, a trained reward model's score, or (as later weeks cover) a verifiable check like "did the code pass its unit tests."

## Math explained step by step

Make explicit the discrete-versus-continuous tension this mapping resolves, since it is the single most common point of confusion when first encountering RL for LLMs.

**Step 1 — the linguistic landscape is fundamentally discrete.** A token is either "moon" or it is not; there is no word that is "80% moon and 20% hammer" for the model to output instead. If you shift the model's internal parameters by a tiny amount, the *most likely* token typically doesn't change at all — the output is locally constant, then snaps discontinuously to a different token once the shift is large enough.

**Step 2 — this makes the naive gradient with respect to the outcome undefined.** You cannot compute $\frac{\partial(\text{"moon" vs "hammer"})}{\partial \theta}$ in any useful sense, because the outcome space has no continuous structure to differentiate against — this is the same non-differentiability problem a loaded die's face-number poses, and later weeks return to it via the log-derivative trick explicitly.

**Step 3 — but the *probability* the policy assigns is continuous and fully differentiable.** $\pi_\theta(a_t \mid S_t)$ is a smooth function of $\theta$ — nudging $\theta$ smoothly changes how much probability mass sits on "moon" versus every other token, even though the eventual *sampled* token remains a discrete draw from that distribution.

**Step 4 — RL for LLMs therefore optimizes probability mass, not tokens directly.** The training objective is $\max_\theta \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)]$, and every algorithm covered in the weeks ahead is, underneath its specific machinery, a way of computing $\nabla_\theta \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)]$ using only this smooth, differentiable probability structure — never requiring a gradient through the discrete token choice itself. This is the mathematical bridge that makes "reinforcement learning for language models" a coherent phrase rather than a category error.

## Practical pattern

1. whenever reasoning about an RL-trained LLM behavior, explicitly identify the state (full context so far), the action (next token), and the trajectory (full response) for the specific case at hand — vague reasoning about "the model's behavior" in aggregate obscures where in the generation the actual decision points are;
2. remember that the state must include the *entire* prior context, not just the most recent token, when designing any system (a custom reward model, a debugging harness) that needs to reconstruct what the policy "saw" at a given generation step;
3. when a reward can only be computed on the *complete* response (a human rating, a full-response correctness check), recognize this as a trajectory-level, not per-token, reward — which reintroduces the credit-assignment problem from earlier pages, now at token granularity, and is precisely what the advantage-function and GRPO material in later weeks exists to address;
4. use this mapping as a sanity check on new agentic-RL claims you encounter elsewhere — if a described technique cannot be restated cleanly in terms of state/action/trajectory/reward for an LLM, either it is not really an RL technique, or the mapping hasn't been done carefully.

## Common traps

- trying to compute a gradient directly against the discrete token output, rather than against the smooth probability distribution the policy assigns — a category error that later weeks' log-derivative-trick material exists specifically to prevent;
- defining "state" as only the most recent token rather than the full accumulated context, which silently breaks the Markov property this week's vocabulary insisted a valid state must satisfy;
- conflating a per-token action with a per-trajectory reward without acknowledging the credit-assignment gap between them — this gap is exactly what motivates the advantage function and more sophisticated reward-shattering techniques covered later;
- treating "RL for LLMs" as a fundamentally different discipline from "RL for robots," when in fact it is the identical mathematical framework applied to a different, larger, but still well-defined state and action space.

## Takeaways

- The LLM itself is the agent and holds the policy; the state is the full prompt-plus-generated-tokens-so-far; the action is the next token; the trajectory is the complete response; the reward is a score on that completed response.
- RL for language models never differentiates the discrete token output directly — it differentiates the continuous probability the policy assigns to each candidate token, which is what makes gradient-based training of a fundamentally discrete process possible.
- Because the reward is usually assigned at the trajectory (whole-response) level while actions occur at the token level, the credit-assignment problem reappears here in a new, more granular form — the central technical challenge the next several weeks' algorithms (PPO, DPO, GRPO) are built to solve.
- This is a literal term-for-term mapping, not a loose analogy — every RL concept from earlier pages (state, action, episode, value, policy) applies to LLMs unmodified in its mathematical form.
