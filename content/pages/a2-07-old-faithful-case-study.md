---
id: a2-07-old-faithful-case-study
title: "The Old Faithful Case Study: What a Prompt Can Actually Unlock"
week: 2
topic: "Act III: Prompt Engineering as Agent Design"
order: 7
summary: A single, carefully structured prompt turned an early-2023 GPT model into an autonomous data scientist that performed and interpreted an entire exploratory analysis unassisted — proof that role-based prompting activates dormant capability rather than teaching new skill.
course: ai_agents
---

The strongest argument this week makes for taking prompt engineering seriously isn't an abstract claim about "quality proportional to input" — it's a concrete, checkable case study conducted in early 2023, using GPT-3.5 and early GPT-4, models that predate most of the reasoning-model breakthroughs discussed elsewhere in this course. The task was the Old Faithful geyser dataset — genuinely simple, just two variables: eruption duration and waiting time until the next eruption. The question the case study set out to answer was blunt: could a single, well-structured prompt elicit a sophisticated, professional-grade, multi-step data analysis from a model that most users at the time were treating as a glorified autocomplete?

It could. And the specific shape of what it produced is worth studying closely, because it's the clearest available demonstration that a prompt doesn't teach a model a new skill — it activates a skill the model already had latent inside it, and a sloppy prompt simply leaves that skill dormant.

## Core intuition

The analogy offered for this is a professional SLR camera: a novice using it on "automatic" mode gets mediocre photos, not because the camera lacks the capability for exceptional images, but because unlocking that capability requires deliberate, informed technique. An LLM prompted casually is a camera left on automatic. The Old Faithful case study is what happens when someone actually learns to use the manual settings.

## Why it matters

This matters practically because it recalibrates expectations about what "the model can't do X" claims are actually measuring. Very often, "the model can't do X" is really "the naive prompt I tried couldn't elicit X" — a different and much more fixable problem. The case study is also a warning against the opposite mistake: assuming that because a model is capable of expert-level output, it will produce it by default, without deliberate role and task specification.

## Instructor framing

Have students read the exact CO-STAR structure used in this case study — role, style/tone/audience, explicit response-format constraints, explicit guardrails against fabrication — and then have them predict, before being told, what capabilities showed up in the output. Most students will underpredict. The point isn't to be impressed by 2023-era GPT-4; it's to notice how systematically people underestimate what a properly specified prompt can unlock, which is exactly the mistake this whole unit is trying to correct.

## Worked example

The prompt cast the model as "an expert data scientist with a reputation for methodical and careful exploratory data analysis," required it to reason step by step in a specific order (univariate statistics, then multivariate statistics, then visualization), specified a formal, precise, scientific style and tone for an audience of scientists and engineers, and set explicit guardrails: no external analytical plugins, all claims grounded in the data itself, no fabrication. What came back, unassisted beyond that single prompt, was a model that self-organized the task into exploratory data analysis stages, autonomously selected appropriate visualization types (histograms, scatter plots, box plots), generated working pandas/scikit-learn/matplotlib code as if working in a notebook, computed and correctly interpreted statistics (correlation of roughly $r \approx 0.9$ between eruption duration and waiting time, correctly described as strongly positive), chose colorblind-accessible color palettes without being asked to, and structured the whole write-up like a research paper — introduction, method, results, conclusion. When later asked to perform clustering, it independently applied *two* separate validation methods for choosing the number of clusters — the elbow method and the silhouette score — a best practice the case study notes "many human data scientists often rely on only one method" to actually follow. It then named the resulting clusters intuitively ("quick cycle," "long cycle") and explained what they meant in real-world terms. Finally, changing a single line of the prompt — swapping the assigned role from "data scientist" to "geologist" — produced an entirely different but equally coherent interpretation of the same dataset, this time framed around geothermal mechanics; changing the role again, to "artist," produced a visual rendering instead of a statistical report.

## Math explained step by step

The role-switching result is the most theoretically interesting part of this case study, and it's worth formalizing why a single-line change in role produces such a large, coherent shift in output — this connects directly to the "thousand PhDs behind a curtain" framing from the CO-STAR page.

**Step 1 — model the LLM's output as conditioned on a latent persona variable.** Treat the model's generation as $P(\text{output} \mid \text{prompt}) = \sum_z P(\text{output} \mid z, \text{prompt}) \cdot P(z \mid \text{prompt})$, where $z$ ranges over a large space of latent "personas" or expert framings the model can adopt, and $P(z \mid \text{prompt})$ is how strongly the prompt pulls the model's generation toward each one.

**Step 2 — see what a role assignment does to this distribution.** Explicitly stating "you are an expert geologist" sharply concentrates $P(z \mid \text{prompt})$ on the geologist-adjacent region of persona-space — analogous to setting a very low temperature specifically along the persona dimension, even though token-level sampling temperature is unchanged. Everything downstream — vocabulary choices, which facts get emphasized, what "interesting" means for this analysis — inherits from that concentrated $z$.

**Step 3 — see why this is qualitatively different from teaching new facts.** The dataset itself never changed between the data-scientist and geologist framings — only $z$ shifted. This is direct evidence that the geological interpretation of Old Faithful's eruption patterns was already latent in the model's training (geothermal physics is presumably well represented in general training data), and the role assignment's whole function was to raise $P(z_{\text{geologist}} \mid \text{prompt})$ enough for that latent knowledge to dominate generation, not to inject new knowledge that wasn't there before.

**Step 4 — connect this back to the "quality proportional to prompt" claim.** A vague or absent role assignment leaves $P(z \mid \text{prompt})$ diffuse across many personas, and the resulting output is effectively an average over incompatible framings — data-scientist caution mixed with generic small talk mixed with none of the domain-specific depth any single $z$ would have provided. This is the formal version of "you get a weaker, more generic answer" from an underspecified prompt: it isn't that the model tries less hard, it's that the output is a blend across a wider, less concentrated set of latent personas.

## Practical pattern

1. Before concluding a model "can't" do a sophisticated task, check whether the attempted prompt actually assigned a specific expert role and explicit methodology — a diffuse or role-less prompt systematically underperforms relative to the model's real latent capability.
2. Use role-switching deliberately as an exploration tool: the same dataset or document, reframed under different expert personas (scientist, auditor, skeptic, novice), can surface genuinely different and complementary analyses at negligible additional cost.
3. Pair role assignment with explicit anti-fabrication guardrails ("ground all claims in the provided data; do not speculate") — the case study's guardrail language was a deliberate, explicit mitigation against a known failure mode of the era, and remains good practice regardless of model generation.
4. When you want a specific methodological rigor (like requiring two independent validation methods rather than one), state that expectation explicitly in the objective — the case study's model volunteered dual validation because "careful, methodical" was set as an explicit role trait, not because dual validation is a default behavior.

## Common traps

- Concluding a capability doesn't exist in a model based on a single naive-prompt attempt, when a properly role-and-methodology-specified prompt might reveal it was latent all along.
- Assuming role-switching changes what the model "knows," when it actually changes which of many already-latent capabilities the prompt concentrates generation toward.
- Treating explicit guardrail language ("ground claims in the data, do not fabricate") as optional boilerplate rather than a load-bearing part of the prompt that measurably reduces a known failure mode.
- Failing to specify methodological expectations explicitly (e.g., "use at least two independent validation approaches") and then being surprised when the model defaults to a single, less rigorous method.

## Takeaways

- The Old Faithful case study demonstrates that even an early-2023 model held substantially more latent capability than casual prompting revealed — the bottleneck was prompt specification, not model capability.
- A single-line role change can produce an entirely different, internally coherent expert framing of the same data, because it concentrates the model's generation on a different region of latent "persona space" rather than injecting new knowledge.
- Underspecified prompts produce outputs that are effectively an average across incompatible framings — weaker not because the model tries less, but because no single expert perspective dominates.
- Explicit methodological and anti-fabrication guardrails in the prompt measurably shape output quality and rigor, and are worth treating as a required prompt component, not an optional add-on.
