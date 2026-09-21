---
id: a12-06-the-geometry-of-sft-vs-rl
title: "The Geometry of SFT vs. RL: Why One Breaks the Model and the Other Doesn't"
week: 12
topic: "Act I: Trust Regions and the Reasoning Breakthrough"
order: 6
summary: SFT updates a model along its highest-curvature, most structurally load-bearing directions, risking catastrophic collapse; RL updates it along low-curvature, structure-preserving directions instead — a geometric answer to why RL is safer despite being slower.
course: ai_agents
---

If you wanted to turn an elephant into a giraffe, a few brushstrokes of paint on the hide would not do it — the bone structure, the mass distribution, the entire physiology would need to change. Common sense suggests that inducing something as dramatic as genuine reasoning ability in a language model should require an equally dramatic restructuring of its internals. And yet inspection of RL-fine-tuned reasoning models reveals something bewildering: remarkably few of the model's parameters appear to change at all. This is not a measurement artifact to be explained away — it is a real, specific, geometrically meaningful phenomenon, and this page works through the explanation research has converged on, because it resolves a question that has quietly hung over every "why does RL feel different from SFT" discussion in this course so far.

## Core intuition

Picture the model's learned probability landscape as a sand dune: pre-training builds the dune's mountains and valleys — the overall morphology and architecture of the distribution. Fine-tuning, whichever method you use, moves sand across an *already-built* dune; it should modulate the surface, not level the mountain.

**Supervised Fine-Tuning is aggressive**, driven by strong, explicitly labeled gradients that seek the fastest path to minimize loss — geometrically, this means climbing the dune along its steepest face, the **high-curvature principal directions** of the model's parameter geometry. Forcing updates along these high-tension directions risks destabilizing the entire structure: like digging into a dune's steep face with an earthmover, the wall can simply collapse. This collapse *is* catastrophic forgetting, given a precise geometric description rather than just a behavioral one.

**Reinforcement Learning is comparatively gentle.** Its signal is weaker and sparser, so it cannot afford SFT's aggression; instead it tends to steer along **low-curvature, off-principal directions** — the thin, flat "thickness of the dough" dimensions where the model's geometry is nearly flat and forgiving. This lets RL find genuinely new behavior (reasoning capability) while respecting, rather than demolishing, the pre-trained architecture underneath it.

## Why it matters

This geometric account resolves the paradox directly: DeepSeek-R1, trained via pure RL, gained substantial reasoning capability while apparently sacrificing something narrower — its earlier "political correctness," beginning to output a chaotic mix of English, Mandarin, and other languages as it prioritized raw logical correctness over curated linguistic tidiness. This is a real instance of mode collapse (borrowing probability mass from one region, linguistic tidiness, to feed another, logical correctness) — but critically, it did *not* trigger the broader, structural catastrophic forgetting that similarly aggressive SFT would risk. The geometric explanation is precise about why: RL's low-curvature updates can still cause *some* mode collapse in narrow, off-principal-adjacent dimensions, without threatening the high-curvature, structurally load-bearing dimensions that hold the model's core knowledge and capability together.

## Instructor framing

Introduce the "Three Gate Theory" as the organizing frame for this whole page, since it names the three separate pieces this explanation needs, and students benefit from seeing all three named before any one is developed in depth. **Gate 1 — the KL Anchor:** the dissipative, tethering force from earlier pages, preventing drift too far from the pre-trained starting point. **Gate 2 — the Geometry of Intelligence:** the principal-versus-off-principal curvature distinction this page's core intuition develops, which is the deepest and most novel piece. **Gate 3 — the Illusion of Sparsity:** the observation that "few parameters change" is partly a measurement artifact of low-precision arithmetic (FP16), not solely a geometric fact — raising the learning rate or switching to FP32 makes far more parameters show measurable movement, meaning some of the apparent sparsity is a resolution limit of the hardware, not a physical property of the learning process itself.

## Worked example

To make "principal direction" concrete rather than abstract, picture applying a matrix transformation to a sphere of perfectly isotropic (uniformly spread) data — the matrix stretches that sphere into an ellipsoid. The **principal directions** (eigenvectors) are the axes of maximum stretch — the directions carrying the dominant, highest-magnitude features of whatever transformation the model's weights represent. The **off-principal directions** are the vast, nearly flat, low-energy subspaces where the data (and the model's sensitivity to changes there) is comparatively inert — pictured as the enormous flat area of a rolled-out roti (flatbread) compared to its negligible thickness: two dominant, high-curvature dimensions, and one nearly negligible, low-curvature dimension.

SFT's aggressive, high-magnitude gradient updates concentrate precisely in the high-curvature principal directions — the equivalent of trying to reshape the roti by pressing hardest exactly where it's already thinnest and most structurally fragile. RL's updates, driven by a much weaker and sparser signal, instead diffuse into the roti's vast flat area — the off-principal directions — finding room to encode new behavior (a "hidden target" reachable via a gentle valley around the base of a hill, rather than by climbing straight over its steepest peak) without disturbing the load-bearing structure.

## Math explained step by step

Work through why sparsity of visible parameter change is partly real geometry and partly a precision artifact, since conflating the two is the most common misreading of this result.

**Step 1 — the geometric claim.** If a model's parameter-space sensitivity is captured by some local curvature matrix (loosely, a Hessian or its low-rank approximation), its eigenvectors with large eigenvalues are the principal directions — small movements along them produce large changes in model behavior, and are exactly where pre-training encoded its most load-bearing structure. Eigenvectors with tiny eigenvalues are off-principal — large movements along them produce comparatively small behavioral changes, making them a "safer" place for a fine-tuning update to occur without destabilizing the model.

**Step 2 — SFT's implicit direction.** A high-magnitude, low-noise SFT gradient, seeking the fastest loss reduction, will naturally align with whatever directions most efficiently reduce loss — typically the high-eigenvalue principal directions, since moving along them produces the largest per-unit-effort change in output behavior. This is efficient for the target task and dangerous for everything else riding on the same directions.

**Step 3 — RL's implicit direction.** A much weaker, sparser RL gradient (recall the "rollout-inefficient" characterization from earlier pages) cannot reliably push hard against high-curvature directions without the noise in its signal producing wildly unstable updates — in practice, the KL-anchored, clipped updates from GRPO/PPO end up concentrated in the flatter, off-principal directions, where a given step size produces a smaller, more controllable, more reversible behavioral change.

**Step 4 — the precision artifact, quantified.** Suppose an off-principal-direction update genuinely shifts a parameter from $2.151$ to $2.153$ — real movement, but below FP16's effective resolution, which may round both to $2.15$. Observing "no change" in that parameter under FP16 measurement is a **measurement floor**, not evidence the parameter didn't move. The paper's own diagnostic — artificially increasing the learning rate, or switching to FP32 — makes this same movement visible, confirming that some (not all) of the observed "sparsity" of change under RL is an artifact of the numerical precision used to observe it, layered on top of the genuinely real geometric preference for off-principal-direction updates.

## Practical pattern

1. when explaining or predicting fine-tuning risk, use the principal/off-principal curvature framing rather than a purely behavioral description ("SFT is aggressive, RL is gentle") — the geometric account explains *why* the behavioral pattern holds and predicts when it might not (e.g., an SFT run with a very small learning rate can behave more like RL geometrically, and vice versa);
2. don't over-interpret "few parameters visibly changed" as proof that a training run had minimal effect — check whether the observation was made at a precision level (FP16) that could be masking genuine off-principal movement, per Gate 3;
3. when an RL-trained model shows a narrow, specific mode collapse (like DeepSeek-R1's language mixing), diagnose it as a targeted trade-off in a specific off-principal-adjacent dimension rather than assuming it signals the onset of broader catastrophic forgetting — the geometric account predicts these are different failure classes with different scopes;
4. combine this page's geometric intuition with the earlier KL-anchoring practice explicitly — the KL term (Gate 1) and the natural low-curvature bias of RL updates (Gate 2) are two separate, complementary reasons RL training tends to preserve pre-trained structure, and neither alone is the whole explanation.

## Common traps

- assuming SFT is simply "more effective" than RL because it changes more visible parameters faster, without accounting for the fact that this same aggressiveness is precisely what risks catastrophic, structure-collapsing forgetting;
- interpreting a narrow mode collapse (like language mixing under pure RL) as evidence that RL is just as prone to catastrophic forgetting as SFT, when the geometric account predicts and locates this as a much narrower, off-principal-direction phenomenon;
- treating "RL barely changes any parameters" as proof that RL training had little real effect, when some of that apparent sparsity is a numerical-precision artifact rather than a true absence of movement;
- attempting to accelerate RL training by deliberately forcing updates into principal directions (an approach some LoRA variants have tried) — this violates the very geometric property that makes RL structure-preserving in the first place, and the research this page summarizes found it counterproductive.

## Takeaways

- Pre-training builds a model's geometric "dune" — its overall probability landscape structure; fine-tuning moves sand across that dune, and *how* it moves the sand determines whether the dune survives.
- SFT's aggressive, high-magnitude updates concentrate in high-curvature principal directions — efficient for the target task, but exactly where catastrophic forgetting geometrically originates.
- RL's weaker, KL-anchored updates naturally diffuse into low-curvature, off-principal directions, preserving the model's core structure while still encoding genuinely new capability — the geometric explanation for why RL is robust despite being slower and noisier than SFT.
- Apparent "sparsity" of parameter change under RL is partly real (the off-principal geometric bias) and partly a measurement artifact of low-precision arithmetic — both pieces are needed for a complete explanation, and conflating them is a common misreading of the result.
