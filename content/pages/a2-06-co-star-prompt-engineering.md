---
id: a2-06-co-star-prompt-engineering
title: "CO-STAR and the Thousand PhDs Behind the Curtain"
week: 2
topic: "Act III: Prompt Engineering as Agent Design"
order: 6
summary: An LLM behaves like a thousand experts behind a curtain, and a system prompt is how you summon a specific one — the CO-STAR framework (Context, Objective, Style, Tone, Audience, Response format) structures that summoning into something precise and repeatable.
course: ai_agents
---

There's a useful, slightly theatrical image this week offers for what a large language model actually is: a thousand PhDs standing behind a curtain, each representing deep expertise in a different domain, waiting to be called forward. When you write a system prompt, you are not teaching the model something it doesn't know — you are choosing, with the words you write, *which* of those thousand experts steps out from behind the curtain to answer you. Write "you are an expert sports journalist" and the sports-journalist expert steps forward. Write nothing in particular and you get some unspecified, averaged-out blend of all of them, which is usually a much weaker response.

The CO-STAR template exists to make that summoning deliberate rather than accidental. It's a structured checklist — Context, Objective, Style, Tone, Audience, Response format — developed by the Singapore government and now widely used for writing system prompts, and the case for using it isn't aesthetic. The difference between a naive prompt and a properly CO-STAR-structured one is described in this week's material as "day and night," and the Old Faithful case study exists specifically to make that claim checkable rather than just asserted.

## Core intuition

The quality of an LLM's output is directly, measurably proportional to the quality and structure of its input prompt — not because the model "tries harder" for a better prompt, but because different phrasings genuinely activate different regions of the model's learned representation, summoning a sharper, more specialized persona and task frame rather than a vague, averaged one.

## Why it matters

This reframes prompt engineering as something closer to a precise communication protocol than a soft skill. The recurring misconception this week pushes back on hardest is that prompting is "just English" and therefore trivial — dismissing it, the material argues, is like dismissing Einstein's contribution because "he just wrote one equation." The value isn't in the length of the input; it's in the precision of the specification, and precision in natural language turns out to be exactly as rare and valuable as precision in any other engineering medium.

## Instructor framing

Have students write the same task twice: once as a naive, single-sentence instruction ("write an editorial on this topic"), and once fully specified through CO-STAR (role, objective, style, tone, audience, and response format all explicit). Then have them compare outputs side by side without being told which is which, and guess. The exercise works because the gap is usually obvious even to someone who hasn't yet internalized why — which is the fastest way to make the CO-STAR discipline feel earned rather than imposed.

## Worked example

Walk through the CO-STAR breakdown exactly as applied to building a news-editorial agent, since it's the running example this week's project is built around. **Context (C)**: "You are an expert sports journalist and editor," plus examples of high-quality output and explicit guardrails. **Objective (O)**: "Relevance-rank news items based on significance and write an editorial on the top five." **Style (S)**: formal, sarcastic, nerdy, explanatory — whatever manner of writing fits the product. **Tone (T)**: a separate axis from style — you might want a scientific *style* delivered with a friendly *tone*, which is a genuinely useful distinction most naive prompts collapse into one setting. **Audience (A)**: content for children reads nothing like content for domain experts, and specifying this changes vocabulary, assumed background, and pacing. **Response format (R)**: plain text or JSON, a target length, a target language variant (American versus British English). Filling all six in deliberately, rather than defaulting most of them, is what separates a CO-STAR prompt from a naive one — and the CO-STAR template is explicitly meant for *system* prompts, the part of the interaction that persists across every subsequent user turn.

## Math explained step by step

Meta-prompting — the practice of using a stronger "big brain" model to iteratively critique and refine your own prompt — has a convergence structure worth being explicit about, since "iterate at least three times" is a specific, checkable recommendation, not an arbitrary ritual.

**Step 1 — model each refinement iteration as reducing prompt ambiguity.** Let $A_i$ be a measure of your prompt's remaining ambiguity after $i$ refinement iterations (informally: the number of edge cases or misreadings a careful reviewer could still find). Each meta-prompting pass reduces this by some fraction: $A_{i+1} = \rho \cdot A_i$ for some $\rho < 1$ representing how effective each critique-and-revise cycle is.

**Step 2 — see why iteration count matters more than any single pass's quality.** After $n$ iterations, remaining ambiguity is $A_n = \rho^n \cdot A_0$ — even a fairly weak per-iteration improvement ($\rho = 0.7$, say) compounds: three iterations get you to roughly $34\%$ of the original ambiguity, a meaningful reduction that a single, even very careful, first pass is unlikely to match, because a single reviewer (human or model) tends to find and fix the *most obvious* ambiguities first, leaving subtler ones for a second and third look with fresh eyes.

**Step 3 — see why the recommended minimum of three iterations is a reasonable stopping heuristic.** Diminishing returns set in as $A_i \to 0$: once a prompt's remaining ambiguity is already small, further iterations yield smaller absolute improvements for the same review effort. Three iterations is empirically where much of the improvement curve's early, high-value region has typically been captured for prompt-refinement tasks of the length and complexity this material describes, without yet paying for the flat tail of diminishing returns.

**Step 4 — connect this to the "must do / avoid / never do" language recommendation.** The material notes that reasoning models respond strongly to sharpened, emphatic language and structural markers (symbols, emphasis) — this is a way of making each unit of $\rho$ larger per iteration, since blunt, hedged language ("try to," "consider") leaves more ambiguity per review pass than sharp, unambiguous imperatives do.

## Practical pattern

1. Structure every non-trivial system prompt explicitly through all six CO-STAR fields — Context, Objective, Style, Tone, Audience, Response format — rather than defaulting fields you haven't thought about; an unspecified field is not neutral, it's an invitation for the model to average across possibilities.
2. Treat style and tone as genuinely separate levers, not one setting — a formal style with a warm tone, or a casual style with an authoritative tone, are both legitimate and different combinations worth choosing deliberately.
3. Use meta-prompting deliberately: draft your best CO-STAR prompt, hand it to the strongest reasoning model available with an explicit request to find ambiguities and improve it, review the result critically rather than accepting it uncritically, and repeat at least three times.
4. Reserve detailed few-shot examples inside the prompt for illustrating format and tone, not for trying to compress your entire task specification into examples — that's a dataset's job (covered later this bootcamp), not a prompt's.

## Common traps

- Leaving CO-STAR fields implicit or default, assuming the model will "figure out" the intended audience, tone, or format — this produces an averaged, generic response rather than the specific persona and framing you actually wanted.
- Treating prompt engineering as trivial "because it's just English," which both underinvests engineering effort in the highest-leverage lever available and misunderstands why precision in natural language is genuinely hard.
- Accepting a meta-prompting model's first revision uncritically instead of reviewing it and iterating, forfeiting most of the compounding ambiguity-reduction the process is designed to produce.
- Using hedged, soft language ("try to be concise," "consider using formal tone") in a system prompt intended for a reasoning model, when sharper, more emphatic phrasing produces measurably stronger adherence.

## Takeaways

- An LLM's output quality is directly proportional to prompt precision — think of the model as many latent experts, and a good prompt as the specific instruction that summons the right one.
- CO-STAR (Context, Objective, Style, Tone, Audience, Response format) structures a system prompt so that none of these dimensions is left to chance or averaged over.
- Style and tone are separate, independently controllable levers — conflating them collapses a genuinely useful degree of control.
- Meta-prompting's value compounds with iteration count; a minimum of three refinement passes is a reasonable heuristic for capturing most of the achievable ambiguity reduction before diminishing returns set in.
