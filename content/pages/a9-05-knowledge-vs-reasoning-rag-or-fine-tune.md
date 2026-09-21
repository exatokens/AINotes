---
id: a9-05-knowledge-vs-reasoning-rag-or-fine-tune
title: "The Fundamental Dichotomy: Knowledge Versus Reasoning"
week: 9
topic: "Act I: The Escalation Ladder for Agent Intelligence"
order: 5
summary: RAG and fine-tuning solve two different problems — RAG injects knowledge the model lacks, fine-tuning instills reasoning or strategy the model cannot derive from any document — and picking the wrong one is the most expensive mistake on the escalation ladder.
course: ai_agents
---

"Should we use RAG or should we fine-tune?" is one of the most common questions an AI engineering team asks, and it is usually the wrong question, because it treats two structurally different remedies as competing options on the same axis. They are not competitors. They answer different diagnoses. The right question is: is the agent missing *information* it could look up, or is it missing an *ability* no document could teach it?

This page draws that line precisely, because getting it wrong is expensive in both directions — fine-tuning a knowledge gap bakes brittle, quickly stale facts into weights that are costly to update, while trying to RAG your way past a genuine reasoning deficit produces a system that retrieves increasingly desperate context and still cannot perform the underlying skill.

## Core intuition

The dichotomy is knowledge versus reasoning. If a problem can be solved by handing the model the right external facts at inference time, use RAG. If a problem requires a new reasoning ability or strategy that no external document could specify, because the space of possible strategies is too vast or too situation-specific to write down, escalate to fine-tuning (and, if necessary, reinforcement learning).

The canonical illustration: fixing a broken vacuum cleaner is a knowledge problem — your first instinct is to find the user manual or a video, i.e., retrieve relevant knowledge and let a competent reasoner apply it. Playing a genuinely unique chess configuration is a reasoning problem — no book can contain the strategy for all possible board positions, since they outnumber the atoms in the observable universe. The ability to reason toward a good move in a *novel* position must be baked into the model itself, not looked up.

## Why it matters

Misdiagnosing which side of this dichotomy a problem sits on wastes both engineering effort and money. RAG has low setup cost but high running cost (every query pays for retrieval, larger context windows, more tokens) — it is a poor fit for a genuine reasoning deficit, because retrieving *more* documents about chess strategy does not make the model a better chess player; strategy is not a fact you can look up, it's a skill that has to live in the weights (or in a policy learned through RL). Conversely, fine-tuning a model on today's product catalog to "teach" it facts that will be stale next month is an expensive, brittle way to store information that a retrieval index updates for free, in real time, with a simple document upload.

## Instructor framing

This page is the theoretical companion to the escalation ladder's Rung 4 versus Rung 5 boundary. When a later multi-agent or Manus-architecture page shows an agent calling a retrieval tool mid-task, connect it back here: that agent's designers correctly diagnosed a knowledge gap and routed it to a sidecar rather than trying to bake transient facts into the model's parameters. When a later page discusses reinforcement learning inducing genuinely new reasoning (DeepSeek's emergent chain-of-thought, for instance), connect it back here too: that is precisely the class of problem RAG structurally cannot touch, because no retrievable document contains "how to reason your way through a novel proof."

## Worked example

Coding agents like Cursor or Codex are a clean real-world instance of *both* sides of the dichotomy operating together, correctly separated. They perform RAG over the user's own codebase — this is the knowledge component, and it is treated as a "no-brainer": indexing and retrieving relevant file context costs comparatively little and directly closes a real information gap (the model has never seen this specific private repository). Separately, the underlying model itself — its ability to reason about program structure, infer intent, and generate correct code — is the expensive, reasoning component, improved through pretraining scale and fine-tuning, not through retrieval. Cursor's own strategic move to fine-tune (and reportedly train) its own models is a bet on the reasoning side of the ledger, made independently of its RAG-over-codebase setup on the knowledge side.

## Math explained step by step

Model total error as two additive, separable components to see why treating them as one lever fails.

**Step 1 — decompose error.** Let total task error $E = E_{\text{knowledge}} + E_{\text{reasoning}}$, where $E_{\text{knowledge}}$ is error caused by missing or outdated facts, and $E_{\text{reasoning}}$ is error caused by an absent skill or strategy, holding facts fixed.

**Step 2 — RAG's effect.** RAG reduces $E_{\text{knowledge}}$ by supplying facts at inference time: $E_{\text{knowledge}} \to E_{\text{knowledge}} \cdot (1 - r)$ for retrieval effectiveness $r \in [0,1]$. Crucially, RAG has approximately zero effect on $E_{\text{reasoning}}$ — retrieved text does not change how the model reasons over it.

**Step 3 — fine-tuning/RL's effect.** Fine-tuning (and especially RL) reduces $E_{\text{reasoning}}$ by changing the model's internal policy: $E_{\text{reasoning}} \to E_{\text{reasoning}} \cdot (1 - f)$ for fine-tuning effectiveness $f$. Fine-tuning has limited and often *negative* long-run effect on $E_{\text{knowledge}}$ compared to RAG, because facts baked into weights go stale and are expensive to refresh — every update requires a new training run rather than a document upload.

**Step 4 — the diagnostic consequence.** If observed error is dominated by $E_{\text{knowledge}}$ (the model reasons fine once given the right facts, but doesn't have them), spending budget reducing $f$ (fine-tuning harder) barely moves total $E$, since $E_{\text{reasoning}}$ was never the bottleneck. Symmetrically, spending budget improving $r$ (retrieving more aggressively) barely moves total $E$ when the bottleneck is $E_{\text{reasoning}}$. The two levers are close to orthogonal, and the practical task is estimating which term of $E$ actually dominates before choosing a lever.

## Practical pattern

1. run a quick diagnostic before choosing a remedy: hand the model the correct facts directly in-context (simulating perfect retrieval) and see if the error disappears — if it does, the deficit is knowledge, route to RAG; if the error persists even with perfect facts supplied, the deficit is reasoning, route to fine-tuning or RL;
2. default to RAG whenever information changes over time (prices, inventory, policies, recent events) — fine-tuning this kind of content creates a maintenance burden that grows every time the underlying facts change;
3. default to fine-tuning or RL only when the target behavior is a *strategy* or *skill* that would need to be re-derived per situation even with perfect information available — negotiation tactics, code architecture judgment, multi-step planning under novel constraints;
4. for systems (like modern coding agents) that plausibly need both, architect them as genuinely separate components — a retrieval sidecar for facts, a fine-tuned or frontier reasoning core for skill — rather than trying to solve both with one lever.

## Common traps

- fine-tuning a model to "know" facts that are inherently time-sensitive, producing a system that is confidently wrong the moment reality changes and expensive to refresh;
- expecting RAG to fix a reasoning deficit by retrieving ever more context, when the actual bottleneck is that the model cannot apply the retrieved information correctly regardless of quantity;
- assuming the knowledge/reasoning line is obvious from the surface of the problem — many tasks that look like "just retrieval" (summarizing a novel argument, synthesizing conflicting sources) actually require nontrivial reasoning over the retrieved material, and pure retrieval quality improvements will plateau early;
- picking RAG purely because it is cheaper to set up (low CapEx) without accounting for the fact that its running cost compounds at high query volume — the next page develops this CapEx/OpEx trade-off directly.

## Takeaways

- RAG and fine-tuning solve different problems: RAG injects retrievable knowledge, fine-tuning (and RL) instills reasoning or strategy that no document can specify.
- Diagnose which term dominates the observed error — supply perfect facts in-context as a test; if the error persists, the deficit is reasoning, not knowledge.
- Time-sensitive information belongs in a retrieval sidecar, not baked into weights, because fine-tuned facts go stale and are expensive to refresh.
- Real systems (coding agents like Cursor) often need both, deployed as genuinely separate components rather than solved by a single lever.
