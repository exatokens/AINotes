---
id: a7-01-model-training-ground-truth-approximation
title: "What Training Actually Is: Chasing an Unknown Function"
week: 7
topic: "Act I: Why Machines Need Training At All"
order: 1
summary: Model training is the search for a function f(x) that approximates an unknown ground-truth function g(x) — a framing that unifies ice-cream sales forecasting, cow-vs-duck classification, and every large language model into one idea.
course: ai_agents
---

Before any conversation about fine-tuning agents makes sense, there's a more basic question worth answering carefully, because it's easy to think you already know the answer and be wrong in a way that causes real confusion later: what is a trained model actually doing? Not mechanically — everyone can recite "gradient descent minimizes a loss function" — but conceptually. What is the *thing* being approximated, and why does calling a model "wrong" not mean what it sounds like it means?

The course's answer starts from a deceptively simple place: reality produces data according to some true, unknown relationship, and modeling is the act of searching for a function that gets close to that relationship without ever having direct access to it. Everything downstream — why fine-tuning works, why it's risky, why frontier models can be so useful despite having no idea what's actually true — traces back to this one framing.

## Core intuition

Assume observed data is produced by some unknown ground-truth function $y = g(x)$ — the *true* relationship between inputs and outputs, whatever that turns out to be. Since $g$ is never directly accessible, the entire project of machine learning is to construct a model $f(x)$ that closely approximates it: $f \approx g$. The famous statistical aphorism applies exactly here — "all models are wrong, but some models are useful" — because $f$ is, by construction, always an approximation built from finite, noisy, incomplete observations, never the ground truth itself. "Wrong" doesn't mean "broken"; it means "necessarily incomplete," and the entire discipline is about managing how much that incompleteness costs you.

## Why it matters

This framing explains phenomena that otherwise look like separate, unrelated facts about machine learning. Why does a model make systematic errors even after extensive training? Because there are unknown unknowns — variables genuinely affecting the outcome that never entered the data at all. The course's own example: an entrepreneur predicting ice-cream sales from temperature builds a model that's genuinely useful for stocking decisions, but wind, rain, and holidays all affect sales too, and none of them are in the model's inputs — the model is not "broken," it's approximating a relationship that has more inputs than the model was given access to.

This same framing scales all the way up to physics and to large language models without changing shape. Newton's Law of Gravity is an extremely useful, extremely accurate model of how objects fall — and it is still, in the strict sense, an approximation of a deeper truth (general relativity, and whatever lies beneath that) that Newton had no access to. An LLM predicting the next token is doing exactly the same thing at enormous scale: approximating the true, unknown statistical structure of human language from a finite sample of text, with no guarantee — and no need — of ever reaching the underlying truth exactly.

## Instructor framing

Introduce the ice-cream and cow/duck examples before anything abstract, and make students state, in their own words, what the unknown ground-truth function $g$ is in each case, and what the unknown unknowns are that $f$ can never fully capture. This is the single most important framing device in the whole fine-tuning unit — students who internalize "we are always approximating something we cannot directly see" will understand why fine-tuning carries real risk (you're perturbing an approximation, not correcting toward ground truth you can verify against) far more readily than students who jump straight into loss functions and gradient descent without this grounding.

## Worked example

Walk both of the course's canonical examples side by side, because they illustrate the same idea across the two basic problem types (regression and classification). For ice-cream sales: $x$ is temperature, $y$ is units sold, and $g(x)$ is the true relationship — whatever combination of physiological and psychological factors makes people buy more ice cream as it gets hotter. The entrepreneur can only observe $(x, y)$ pairs from past sales data, never $g$ itself, and builds $f(x)$ from that data. Model quality here is measured with regression metrics like Mean Squared Error or Mean Absolute Error — how far off, on average, are the model's predictions from the actual observed sales.

For cow-vs-duck classification: $x$ is a set of features (weight, size, feather presence), $y$ is the species label, and $g(x)$ is the true, unknown decision boundary nature actually uses to distinguish the categories humans have named "cow" and "duck." A trained classifier draws its own approximate boundary $f(x)$ separating the observed data points, and its quality is measured differently — accuracy, precision, recall, F1 score — because the underlying problem type (discrete categories, not a continuous quantity) calls for different metrics even though the conceptual structure, approximating an unknown $g$ with a learned $f$, is identical.

## Math explained step by step

State the Universal Approximator Theorem precisely, since it's the mathematical guarantee that makes "we can approximate any $g$" more than wishful thinking.

**Step 1 — the theorem's claim.** A standard feedforward neural network with a single hidden layer, given a sufficient number of neurons, can approximate any continuous function to an arbitrary degree of accuracy. This is a genuine existence guarantee: for any continuous $g$ and any tolerance $\epsilon > 0$, there exists a network architecture and parameter setting $f$ such that $|f(x) - g(x)| < \epsilon$ for all $x$ in the relevant domain.

**Step 2 — why this matters for training, not just architecture design.** The theorem guarantees a suitable $f$ *exists* somewhere in the space of possible networks; it says nothing about how to *find* it. That's what the training loop (forward pass, loss computation, gradient computation via backpropagation, parameter update) is for — it's a search procedure over the space the theorem guarantees contains a good-enough answer.

**Step 3 — the Null Hypothesis boundary case.** The theorem's guarantee is conditional on $g$ actually existing as a meaningful relationship between $x$ and $y$. If the data is genuinely produced by no relationship at all — $x$ and $y$ scattered with no curve or surface for a model to hug — then the Null Hypothesis holds, and no amount of network size or training time will find a useful $f$, because there is no $g$ worth approximating in the first place. This is a boundary condition every practitioner needs to check for before blaming a model's failure on insufficient capacity or training.

**Step 4 — the update rule that performs the search.** Training updates parameters $\theta$ via $\theta_{\text{new}} = \theta_{\text{current}} - \alpha \nabla_\theta L$, where $L$ measures the divergence between $f(x)$'s predictions and observed $y$ values, and $\alpha$ is a step size. Repeated application of this update is the mechanical process by which $f$ is nudged, cooperatively across all its parameters, to converge toward a useful approximation of $g$ — exactly the search the Universal Approximator Theorem guarantees has a good destination, provided a real relationship exists to find.

## Practical pattern

Applying the ground-truth-approximation framing to real modeling decisions:

1. before training anything, ask explicitly what the unknown ground-truth function $g$ is believed to be, and what known unknown-unknowns (unmeasured but plausibly influential variables) exist — this framing surfaces gaps in your feature set before you've spent compute discovering them the expensive way;
2. treat persistent model errors as evidence about missing inputs or an insufficient model class first, before assuming more training or more parameters will fix them — if the error pattern correlates with an unmeasured variable (weather, holidays), no amount of additional training on the existing inputs closes that gap, because the information genuinely isn't in the data;
3. before extensive training investment, sanity-check for the Null Hypothesis case — plot or otherwise inspect whether there's any discoverable relationship at all between your inputs and outputs, since training compute spent chasing a non-existent pattern is compute wasted regardless of model size;
4. choose evaluation metrics that match the problem type (MSE/MAE for continuous regression targets, accuracy/precision/recall/F1 for discrete classification) rather than defaulting to whichever metric is most familiar, since the "close approximation to $g$" framing cashes out differently depending on whether $g$'s output space is continuous or categorical.

## Common traps

- treating "the model is wrong" as evidence of a bug or insufficient effort, rather than the expected, permanent condition of any model, which is always an approximation of an inaccessible ground truth — the right question is "wrong by how much, and does that matter for this use case," not "how do we make it not wrong";
- assuming more training or a bigger model can compensate for missing input variables — if the unknown unknowns (wind, rain, holidays in the ice-cream example) were never in the training data, no amount of additional optimization against the existing inputs recovers that missing signal;
- skipping a basic check for whether a genuine relationship exists in the data at all before investing heavily in model size and training time, risking a costly training run against what is, in truth, the Null Hypothesis case;
- using the wrong metric family for the problem type — applying regression-style error metrics to a classification problem, or vice versa, obscures whether $f$ is actually a good approximation of the relevant $g$.

## Takeaways

- All model training is the search for a function $f(x)$ approximating an unknown, true ground-truth function $g(x)$ — this framing applies identically to ice-cream sales forecasting, animal classification, physics, and large language models, and explains why "the model is wrong" is a permanent condition, not a fixable bug.
- The Universal Approximator Theorem guarantees a sufficiently large single-hidden-layer network can approximate any continuous $g$ to arbitrary accuracy — but this is an existence guarantee, not a discovery procedure; the training loop is the actual search.
- Persistent model error is often a signal of unknown-unknown input variables missing from the data, not insufficient training — and checking for the Null Hypothesis case (no real relationship exists at all) is a cheap sanity check worth doing before any serious training investment.
