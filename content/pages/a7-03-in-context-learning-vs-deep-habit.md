---
id: a7-03-in-context-learning-vs-deep-habit
title: "The Actor Handed a Script vs. the Actor Who Became the Role"
week: 7
topic: "Act II: Fine-Tuning vs Prompting vs RAG"
order: 3
summary: Prompting gives a model a script to improvise from fresh on every call; fine-tuning changes what the model fundamentally is — and that distinction, not model size, is why "agents" built purely on prompts earn the criticism that they're unreliable.
course: ai_agents
---

There's a specific, valid criticism of most agentic systems built today, and it's worth stating plainly instead of softening it: a huge fraction of what gets marketed as an "AI agent" is, underneath, a system prompt wrapped around a frontier LLM. The course doesn't shy away from this — it calls these "prompts fashionably dressed" — and the criticism that follows from it is exactly the one users actually experience: the system works beautifully one moment and produces something subtly wrong the next, with no obvious pattern to when.

This isn't a minor implementation detail. It's a structural consequence of what prompting actually is, mechanically, compared to what fine-tuning is. Getting this distinction right explains both why prompting is often good enough, and why, for specific classes of task, it structurally can't be.

## Core intuition

When you write a system prompt and hand a model both the prompt and the user's data, the model performs in-context learning: it reads the "script" and plays the role for the first time, every single time, improvising fresh from whatever the prompt describes. Nothing about a previous successful run persists into the next one — the model has no accumulated experience of having done this task before, only whatever instructions happen to be sitting in this particular context window.

Fine-tuning is categorically different: the model's underlying parameters change, through repeated exposure to examples of the desired behavior, so the behavior becomes ingrained — a deep habit rather than a freshly-read instruction. The model's "very basic nature changes," in the course's own phrase, because it has genuinely been shown, and adjusted its weights in response to, large numbers of examples of how to behave, rather than being told once, in natural language, what to do.

## Why it matters

The course's acting analogy captures the practical consequence precisely: a prompt-based agent is like an actor handed a script on the morning of the shoot and expected to perform immediately — competent, sometimes even good, but fundamentally improvised, with an error rate that reflects "learning and doing the job for the first time every time the request is invoked." A fine-tuned model is like an actor — the course's example is Ben Kingsley playing Gandhi — who lives and breathes the role until it becomes an inherent part of their nature, correcting mistakes and refining the performance over the course of extended, repeated training rather than a single cold read.

This directly explains the unreliability criticism leveled at prompt-only agents: if every invocation is a fresh cold read, then variance across invocations isn't a bug to be patched with a better prompt — it's the expected behavior of a system that has never actually practiced the task, only been told about it. Fine-tuning attacks this at the root by baking the behavior into the weights themselves, through supervised fine-tuning or reinforcement learning, so the low-error-rate performance doesn't depend on getting a good cold read every time.

## Instructor framing

Have students articulate, before introducing any technical vocabulary, why an actor reading a script cold would be less reliable than an actor who has deeply internalized a role — most students will get this immediately from lived experience of watching performances, without needing any AI-specific framing at all. Then map "cold read" onto in-context learning and "internalized role" onto fine-tuning explicitly, and only after that connection is solid, introduce the specific mechanism (parameter updates via supervised fine-tuning or RL) that makes the analogy literally, not just figuratively, true — the weights really do change, which is precisely what doesn't happen during in-context learning.

## Worked example

A team builds an agent to review children's-park development proposals for safety concerns — environmental impact of a lakeside location, regulatory questions, injury-mitigation details like how pillar-loosening in playground swings is addressed. The prompt-based version writes an increasingly long and detailed system prompt trying to enumerate every category of concern the reviewer needs to catch, hoping thorough instructions substitute for genuine domain expertise. It catches some things reliably and misses others inconsistently — sometimes flagging the lakeside environmental issue, sometimes not, depending on subtle variation in how the proposal document happens to be phrased, because the model is reasoning fresh from the prompt's instructions each time rather than drawing on ingrained, practiced pattern recognition for this specific kind of risk.

A fine-tuned version, trained on many examples of playground-safety review — proposals paired with the specific concerns a domain expert flagged in each — develops something closer to a specialist's "hawk eye" for this category of risk: pillar-loosening concerns, lakeside environmental questions, and similar patterns get caught consistently because the model's weights have been shaped, through repeated exposure, to notice them as a matter of ingrained habit rather than because a lengthy prompt happened to mention them. The system prompt for the fine-tuned version can be short, because the specialization no longer depends on the prompt carrying the full weight of teaching the behavior fresh each time.

## Math explained step by step

Frame the reliability difference as a variance argument, since "unreliable" deserves a precise meaning, not just a vibe.

**Step 1 — in-context learning as a per-call inference.** Each invocation of a prompt-based agent is, mechanically, a single forward pass conditioned on the prompt and input, with the model's weights $\theta$ fixed and unchanged from call to call. The model's output on a given input $x$ is a function $f_\theta(x, \text{prompt})$, where the behavior specific to this task lives entirely in the prompt text, re-interpreted fresh by the same general-purpose weights every time.

**Step 2 — variance sources in the prompt-based case.** Because the task-specific behavior is encoded only in natural language instructions the model must correctly interpret and apply on the fly, output variance across similar inputs depends on how robustly the model's general-purpose weights $\theta$ happen to generalize the prompt's instructions to each specific case — a source of variance that doesn't shrink no matter how many times the same prompt is reused, since nothing about the process changes between calls.

**Step 3 — fine-tuning as a shift in $\theta$ itself.** Fine-tuning updates $\theta \to \theta'$ through gradient descent against examples of the desired behavior, so the task-specific pattern-recognition is now embedded directly in the weights: $f_{\theta'}(x)$ no longer depends on a lengthy prompt correctly steering a general-purpose model each time — the specialization is structural, not instructional.

**Step 4 — why this reduces variance, not just improves average accuracy.** Because the fine-tuned weights $\theta'$ were shaped by many training examples specifically selected to cover the relevant behavior's edge cases, the model's response to novel-but-similar inputs draws on a genuinely learned pattern rather than a single, possibly imperfect, natural-language description of that pattern being re-interpreted from scratch each time — this is the concrete mechanism behind lower run-to-run variance, not merely a claim that fine-tuned models are "better" in some vague sense.

## Practical pattern

Deciding when the reliability gap between prompting and fine-tuning actually matters enough to act on:

1. before reaching for fine-tuning, honestly characterize the failure pattern you're seeing from a prompt-based approach — if errors correlate with subtle input phrasing variation rather than genuine task difficulty, that's the signature of in-context-learning variance the acting analogy predicts, and it's a strong signal fine-tuning (not more prompt engineering) is the right lever;
2. reserve fine-tuning for tasks where consistent, specialized behavior matters enough to justify the upfront training cost — a task tolerant of occasional inconsistency, or one performed rarely enough that cost dominates reliability concerns, may not clear that bar;
3. when fine-tuning is warranted, invest in training examples that specifically cover the edge cases and failure patterns observed from the prompt-based version — the fine-tuned model's reliability gain comes precisely from having "practiced" those cases, not from fine-tuning in the abstract;
4. don't expect a shorter prompt after fine-tuning to be a bug — a genuinely well-fine-tuned model needs less prompt scaffolding precisely because the specialization has moved from the prompt into the weights, which is the intended outcome, not a sign something was lost.

## Common traps

- responding to inconsistent agent behavior by continuing to lengthen and refine the system prompt indefinitely, when the underlying issue is a structural limitation of in-context learning that no amount of additional prompt text fully closes;
- assuming a bigger or smarter frontier model automatically solves the reliability problem — a larger model still performs in-context learning on every call unless it's been fine-tuned, so size alone doesn't change the fundamental "fresh cold read each time" dynamic;
- fine-tuning without first confirming the failure pattern actually looks like in-context-learning variance (inconsistency across similar-but-differently-phrased inputs) rather than a different problem entirely, like missing or wrong information the model was never given access to (which RAG, not fine-tuning, addresses);
- treating "prompts wearing fancy dresses" as an insult to avoid rather than an accurate description of a real architectural choice that's often perfectly appropriate — many tasks genuinely don't need fine-tuning's reliability gain, and building it in anyway adds cost without matching benefit.

## Takeaways

- In-context learning (prompting) has the model improvise fresh from instructions on every single call, with no accumulated practice carried between invocations — this is the acting-analogy's "cold read," and it's the structural reason prompt-only agents show run-to-run inconsistency.
- Fine-tuning changes the model's actual weights through repeated exposure to examples, embedding the desired behavior as a deep habit rather than an instruction to be re-interpreted each time — the acting-analogy's "lived-in role."
- The decision to fine-tune should be driven by whether observed unreliability specifically matches the in-context-learning variance pattern (inconsistency across similar inputs) — if so, fine-tuning targets the actual mechanism; if the real problem is missing information, RAG is the correct fix instead, not fine-tuning.
