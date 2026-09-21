---
id: a8-05-peft-lora-mechanics
title: "LoRA: The Small Change That Doesn't Touch the Original"
week: 8
topic: "Act II: Surgical Fine-Tuning — From Full Updates to LoRA"
order: 5
summary: LoRA freezes the entire base model and learns only a small, low-rank perturbation alongside it — a rudder steering a frozen engine rather than rebuilding the engine, which is why adapters are cheap, fast, and stackable.
course: ai_agents
---

Even selective layer fine-tuning still directly modifies the model's actual weights, layer by layer — and modifying weights, however surgically targeted, always carries some forgetting risk, because the original values are gone once overwritten. Parameter-Efficient Fine-Tuning takes a different approach entirely: don't touch the original weights at all. Freeze the whole base model, and learn a small, separate, additive correction alongside it. If the correction turns out to be wrong or unwanted, the original model underneath is untouched and fully recoverable — you just remove the correction.

LoRA (Low-Rank Adapters) is the most popular way to implement this idea, and it's built on a specific, elegant mathematical insight: the *change* a fine-tuning task actually needs to make to a layer's behavior is usually much simpler — lower-dimensional — than the layer itself, even when the layer has millions of parameters. This page works through why that insight holds and what it buys you in practice.

## Core intuition

PEFT methods emerged specifically to combat industrial capture — a period when only large, well-resourced organizations could afford full fine-tuning's compute requirements. The core PEFT move is to leave the original model's parameters completely frozen and introduce a small, trainable "sidecar" that adjusts the frozen model's behavior without ever changing its underlying weights.

**Soft prompting** (prefix-tuning) is the simplest version: learn a small set of auxiliary vectors prepended to the input, trained via backpropagation to steer the frozen model's output in a desired direction — a rudder, not an engine modification, since the large frozen model still provides all the actual computational power and the small learned vectors only nudge where that power gets directed.

**LoRA** goes further, targeting the weight matrices themselves but in a parameter-efficient way: it exploits the empirical observation that the perturbation a fine-tuning task needs to make to a weight matrix $M$ is low-rank — it can be well-approximated by the product of two much smaller matrices, rather than requiring a full update to every entry of $M$.

## Why it matters

The vibrating-circle analogy explains why low-rank works at all, intuitively: small vibrations of a three-dimensional circle can be fully described by unrolling them into a much simpler one-dimensional wave — the perturbation itself, even though it's acting on a complex object, is structurally much simpler than the object it's perturbing. LoRA makes the identical bet about fine-tuning: the *change* a specific fine-tuning task needs isn't as complex as the full weight matrix it's modifying, so it can be captured with far fewer parameters than the matrix itself contains.

This has direct, practical consequences. Instead of updating every entry of a weight matrix $M$ with potentially millions of parameters, LoRA freezes $M$ entirely and adds a parallel low-rank path: $Y = M(x) + B(A(x))$, where matrix $A$ projects the input down to a very low-rank space (say, 4 dimensions from an original 1,000) and matrix $B$ projects it back up to the original dimension. Only $A$ and $B$ are trained — often a few thousand parameters where full fine-tuning would have required a million — making LoRA dramatically faster and cheaper, while $M$, the original model's knowledge, remains completely untouched and therefore immune to being damaged by this specific fine-tuning run.

A further practical benefit follows directly from the additive structure: LoRA adapters are stackable. Because each adapter is just an additive correction on top of the frozen base, multiple LoRAs trained independently — for different styles, tasks, or domains — can be combined on the same frozen base model, the way the course describes generative-art users combining an artist-style adapter, a texture adapter, and a mood adapter like flavors of ice cream, without any of them interfering with the underlying frozen model or, in principle, with each other.

## Instructor framing

Use the British-vs-American-spelling example as the cleanest possible illustration of why LoRA's small, additive correction is sufficient for many real fine-tuning needs: teaching a model to consistently write "center" instead of "centre" doesn't require retraining its entire understanding of English — it requires a small, surgical nudge, exactly the shape LoRA's $B(A(x))$ term provides while $M(x)$, the model's core language competence, stays completely intact. This example should land before the matrix mechanics, so students already believe the *conclusion* (small corrections are often sufficient) before working through *why* the low-rank structure makes that mathematically efficient to implement.

## Worked example

A team wants to adapt a general code-completion model to consistently follow their company's specific internal coding conventions — variable naming patterns, a preferred logging library, particular error-handling idioms. This is a genuinely narrow behavioral correction layered on top of the model's already-extensive general programming competence, structurally similar to the British/American spelling case but in a technical domain.

Using LoRA, the team freezes the entire base model and trains small adapter matrices attached to select weight layers, using a modest set of internal code examples reflecting the desired conventions. Training completes quickly, using a small fraction of the memory and time full fine-tuning would require, since only the small $A$ and $B$ matrices are being optimized. If the team later needs a *second* specialization — say, adapting the same base model separately for a different subsidiary's slightly different conventions — they can train a second, independent LoRA adapter rather than fine-tuning a whole separate copy of the base model, and in principle can even combine adapters if some conventions are shared across contexts, exactly the stacking behavior the generative-art LoRA community discovered for combining visual styles.

## Math explained step by step

Work through the low-rank decomposition explicitly, since "$A$ projects down, $B$ projects back up" deserves the actual dimensional bookkeeping that makes the parameter savings concrete.

**Step 1 — set up the frozen weight matrix and the additive correction.** Let $M \in \mathbb{R}^{d \times d}$ be a frozen weight matrix from the base model (dimension $d$, potentially in the thousands). LoRA introduces $A \in \mathbb{R}^{r \times d}$ and $B \in \mathbb{R}^{d \times r}$, where $r \ll d$ is the chosen rank (often single digits to low tens). The adapted output is $Y = M(x) + B(A(x))$, where $M$ remains frozen and only $A$, $B$ are trainable.

**Step 2 — count the parameters saved.** Full fine-tuning of $M$ would require updating $d \times d$ parameters. LoRA's trainable parameters total $r \times d$ (for $A$) plus $d \times r$ (for $B$), which is $2rd$ — compare this to $d^2$ for full fine-tuning. For $d = 1000$ and $r = 4$: full fine-tuning updates $1{,}000{,}000$ parameters; LoRA updates $2 \times 4 \times 1000 = 8{,}000$ — a $125\times$ reduction in trainable parameter count for this single matrix, which is the concrete arithmetic behind "a few thousand parameters instead of a million."

**Step 3 — verify the composition still produces a meaningful output.** $B(A(x))$ is the composition of a down-projection ($A$: $d \to r$ dimensions) followed by an up-projection ($B$: $r \to d$ dimensions), producing an output back in the original $d$-dimensional space, compatible for addition with $M(x)$. The rank-$r$ bottleneck in the middle is precisely the low-rank assumption made concrete: whatever correction the fine-tuning task needs is being forced through an $r$-dimensional information bottleneck, which is only a reasonable design if the true needed correction really does have low intrinsic complexity — exactly the vibrating-circle assumption.

**Step 4 — the stacking argument, formalized.** Because the adaptation is purely additive ($Y = M(x) + B_1(A_1(x)) + B_2(A_2(x)) + \ldots$ for multiple independently-trained adapters), combining $k$ LoRA adapters costs only the sum of their individual small parameter counts, $\sum_i 2 r_i d$, still vastly smaller than $d^2$ even for a substantial number of stacked adapters — this is the arithmetic reason stacking many small, independently-trained adapters remains cheap even as their number grows, unlike stacking would be for full separately-fine-tuned models.

## Practical pattern

Deciding when and how to use LoRA versus fuller fine-tuning approaches:

1. default to LoRA (or another PEFT method) for most fine-tuning needs, reserving full or selective-layer fine-tuning for cases with strong evidence (via the gradient-heatmap diagnostic from the previous page) that the required change genuinely exceeds what a low-rank correction can represent;
2. choose the rank $r$ deliberately as a trade-off: a smaller $r$ means fewer trainable parameters and lower risk of overfitting the adapter to a small fine-tuning dataset, but may be too constrained to capture a genuinely complex correction — start small (the course mentions rank $r=8$ as a common starting point) and increase only if evaluation shows the adapter is under-fitting the target behavior;
3. use established libraries (`peft`, or SaaS platforms like Unsloth or Fireworks.ai) rather than implementing LoRA's matrix mechanics from scratch, since these tools handle the practical details (which layers to attach adapters to, hyperparameter defaults) that would otherwise require significant additional experimentation;
4. take advantage of stacking for genuinely modular specialization needs — separate adapters for separate, potentially-combinable concerns (a style adapter, a domain adapter) rather than training one large adapter trying to capture everything at once, mirroring the generative-art community's flavor-combining pattern;
5. keep the frozen base model as the single shared asset across all your adapters — this is also an infrastructure win, since serving many LoRA-adapted variants of the same base model requires storing only one copy of the large frozen weights plus many small adapter files, rather than many full copies of a fine-tuned model.

## Common traps

- defaulting to full or selective-layer fine-tuning out of familiarity, without checking whether the target correction is plausibly low-rank (as most narrow behavioral or stylistic corrections are) and would therefore be well-served by LoRA at a fraction of the cost;
- choosing an unnecessarily large rank $r$ "to be safe," which erodes LoRA's core efficiency advantage and can reintroduce overfitting risk on small fine-tuning datasets without a corresponding capability benefit;
- assuming stacked LoRA adapters always compose cleanly with no interference, when adapters trained independently for genuinely conflicting behavioral goals can still interact in unexpected ways once combined — stacking works well for complementary concerns (style plus texture) but isn't an unconditional guarantee for any combination;
- implementing LoRA's matrix mechanics from scratch when mature, well-tested libraries already handle the practical details, spending engineering effort on infrastructure that adds no value over existing tools.

## Takeaways

- Parameter-Efficient Fine-Tuning freezes the entire base model and learns only a small, additive "sidecar" correction, so the original model's knowledge is never overwritten and remains fully recoverable if the adaptation turns out to be unwanted.
- LoRA's low-rank decomposition ($Y = M(x) + B(A(x))$, with $A$ and $B$ far smaller than the frozen matrix $M$) exploits the empirical fact that most fine-tuning corrections are structurally simple relative to the full weight matrix they're modifying — cutting trainable parameters by two or more orders of magnitude in typical cases.
- Because LoRA adapters are purely additive, they're stackable: multiple independently-trained adapters for different concerns (style, domain, task) can be combined on the same frozen base model at a fraction of the cost of training or storing multiple fully fine-tuned model copies.
