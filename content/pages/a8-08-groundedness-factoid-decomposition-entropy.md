---
id: a8-08-groundedness-factoid-decomposition-entropy
title: "Pinning Every Claim to Its Evidence"
week: 8
topic: "Act III: Trust at the System Level"
order: 8
summary: Grounding a RAG answer means decomposing it into individual factoids and pinning each to specific retrieved evidence — and rising token-level entropy during generation is a real-time signal that the model is about to hallucinate.
course: ai_agents
---

Everything this week has been about building and fine-tuning the models and agents that make up a system — but a system full of well-trained, well-specialized agents can still produce an answer that sounds confident and is quietly wrong, because generation and truthfulness are not the same property. A model can synthesize fluent, well-structured prose from retrieved evidence and still, in the process, introduce a specific number or claim the evidence never actually supported. This is the hallucination problem in its most dangerous form: not an obviously nonsensical answer, but a plausible one with one wrong detail buried inside it.

The fix the course lays out has two complementary halves: a structural technique — decompose the answer into its smallest checkable pieces and verify each one against actual retrieved evidence — and a real-time signal — monitor the model's own uncertainty as it generates, since a specific statistical pattern in that uncertainty is a genuine early-warning sign of an impending hallucination.

## Core intuition

**Factoid decomposition and evidence pinning**: break a generated answer down into its constituent factoids — the smallest possible, self-contained statements of fact it contains — and then check whether each individual factoid can be pinned to a specific piece of retrieved evidence. A factoid that cannot be pinned to anything in the retrieved documents is an ungrounded assertion, and it signals one of two distinct problems: either the model drew on its own parametric memory (knowledge from training, not from the evidence it was actually given, which the system's design forbids) or the model genuinely hallucinated the fact, generating something that isn't true anywhere.

**Entropy checking**: monitor the statistical uncertainty (entropy) of the model's output token distribution as it generates. Entropy is a direct measure of how spread out the model's probability distribution over possible next tokens is at each step; if entropy rises above a threshold during generation, it's a signal that the model's own confidence in what it's producing is dropping — a real-time, in-process warning sign of an impending hallucination, distinct from and complementary to the after-the-fact factoid-checking approach.

## Why it matters

The Berlin example makes factoid decomposition concrete and shows why granularity matters: "Berlin is the capital of Germany. It is the most populous city of the nation, with a population of 3.8 million people" decomposes into three separate factoids — $f_1$: Berlin is the capital of Germany; $f_2$: Berlin is the most populous city of Germany; $f_3$: Berlin's population is 3.8 million. Checking the *whole sentence* against retrieved evidence as one unit would miss a case where $f_1$ and $f_2$ are well-supported but $f_3$'s specific number is wrong or unsupported — decomposition to the individual-factoid level is what makes a single incorrect number, buried inside an otherwise accurate answer, actually catchable.

Handling contradictory retrieved information is a related, practical case this framework directly addresses: if retrieval surfaces two documents disagreeing on Berlin's population — one saying 5.6 million, another 6.9 million — factoid decomposition surfaces this as conflicting evidence for the population factoid specifically, which triggers a refinement loop to resolve the discrepancy (checking source recency, authority, or simply flagging the uncertainty to the user) rather than the system silently picking one number and presenting it with unwarranted confidence.

## Instructor framing

Walk the Berlin example decomposition explicitly on the board or slide, factoid by factoid, and have students identify which retrieved passage (if any) would need to support each one — this concrete exercise is what makes "pin each factoid to evidence" a specific, checkable procedure rather than a vague aspiration to "be more careful." Then introduce entropy checking as a genuinely different kind of signal — not "check the output after it's generated" but "watch the generation process itself for a warning sign" — and make clear these are complementary, not competing, techniques: factoid decomposition catches problems after generation completes; entropy checking can catch problems as they're forming, potentially allowing generation to be aborted before a hallucinated claim is even fully produced.

## Worked example

A RAG system answering "What was DeepSeek's reported reduction in SFT labeling requirements, and what technique enabled it?" generates: "DeepSeek reduced SFT labeling by 80-90% using GRPO, a rule-based reward model, applied after fine-tuning on a small set of Chain-of-Thought examples." Decomposed into factoids: $f_1$ — DeepSeek reduced SFT labeling by 80-90%; $f_2$ — GRPO is a rule-based reward model; $f_3$ — GRPO was applied after fine-tuning on Chain-of-Thought examples; $f_4$ — the Chain-of-Thought fine-tuning set was small. Each factoid gets checked against the actual retrieved passage about DeepSeek's pipeline — in this case, all four are directly supported, and the answer is confidently grounded.

Now suppose the model, in the same answer, had added an unsupported elaboration: "...making DeepSeek's approach roughly ten times cheaper than OpenAI's comparable training pipeline." This is a new factoid, $f_5$, and it fails to pin to any retrieved evidence — the retrieved documents say nothing about OpenAI's training costs at all. This is exactly the kind of confident-sounding, plausible-but-unsupported addition that a whole-sentence groundedness check might miss (the sentence as a whole reads fluently and consistently with the rest of the accurate answer) but that factoid-level decomposition catches specifically, flagging $f_5$ for rejection or requiring the answer to be reformulated without it.

## Math explained step by step

Formalize entropy as an uncertainty measure, since "watch the entropy" needs a precise definition to be operational as an engineering signal.

**Step 1 — define entropy over the model's output distribution.** At each generation step, the model produces a probability distribution $P(\text{token})$ over its vocabulary for the next token. Shannon entropy over this distribution is

$$H = -\sum_{i} P(\text{token}_i) \log P(\text{token}_i)$$

**Step 2 — interpret the boundary cases.** If the model is highly confident — nearly all probability mass concentrated on one token — entropy $H$ is close to zero, since $P \approx 1$ for that token makes $\log P \approx 0$ and all other terms have $P \approx 0$. If the model is maximally uncertain — probability spread roughly evenly across many plausible tokens — entropy is high, approaching $\log(\text{vocabulary size})$ in the most extreme case.

**Step 3 — connect rising entropy to hallucination risk.** A model generating a well-grounded claim, drawing on clear, unambiguous evidence, tends to be confident about the specific words and numbers it produces — low entropy. A model about to produce a fabricated or poorly-supported claim often shows measurably higher entropy at the specific tokens carrying the fabricated content, because there's no strong evidential signal pulling its distribution toward one specific answer — it's effectively guessing among several plausible-sounding continuations, and that internal uncertainty is directly visible in the entropy of its own output distribution, even before any external fact-check occurs.

**Step 4 — the operational threshold decision.** Setting an entropy threshold above which generation is flagged or aborted is a genuine precision/recall trade-off, structurally identical to the guardrail threshold trade-offs discussed elsewhere in this course: a low threshold (aggressive flagging) catches more genuine hallucinations but also flags more false positives — confident-sounding but genuinely uncertain phrasing that happens to be accurate; a high threshold misses more genuine hallucinations in exchange for fewer false interruptions. The right threshold depends on the same asymmetric-cost reasoning used throughout this course: how costly is a missed hallucination in this specific application, versus how costly is an unnecessarily aborted, accurate generation.

## Practical pattern

Building a groundedness and hallucination-control layer for a RAG-based agentic system:

1. decompose every generated answer into its individual factoids before checking groundedness — never check a multi-claim answer as a single unit, since this hides exactly the partial-accuracy failure mode (mostly right, one wrong number) that decomposition is specifically designed to catch;
2. attempt to pin each factoid to a specific retrieved passage, and treat any factoid that cannot be pinned as either drawn from forbidden parametric memory or outright hallucinated — reject or flag it rather than assuming a plausible-sounding claim is safe by default;
3. when retrieved evidence is genuinely contradictory across sources for a given factoid, trigger an explicit refinement loop (check source authority or recency, or present the discrepancy transparently to the user) rather than silently resolving the conflict by picking one value;
4. instrument the generation process to monitor token-level entropy in real time where your serving infrastructure supports it, and use rising entropy as a trigger to abort or flag generation before a fully-formed hallucinated claim is even produced, complementing the after-the-fact factoid check rather than replacing it;
5. tune the entropy-flagging threshold based on your application's specific cost asymmetry between missed hallucinations and false-positive interruptions, rather than adopting a default threshold from a different domain with a different risk profile.

## Common traps

- checking groundedness at the whole-answer or whole-sentence level rather than the individual-factoid level, which systematically misses cases where an answer is mostly accurate but contains one unsupported claim buried among several supported ones;
- treating an ungrounded factoid as automatically a "hallucination" without distinguishing whether it came from forbidden parametric memory (the model knew something true but wasn't supposed to use unretrieved knowledge) versus genuine fabrication (the claim isn't true anywhere) — these have different remediation paths even though both fail the pinning check;
- silently resolving contradictory retrieved evidence by picking one value without surfacing the discrepancy, rather than triggering the refinement loop the course specifically recommends for this case;
- relying solely on after-the-fact factoid checking without any real-time entropy monitoring, missing the opportunity to catch and abort a hallucination while it's still forming rather than only after the full (potentially costly-to-generate) answer is complete.

## Takeaways

- Factoid decomposition breaks a generated answer into its smallest checkable claims and pins each one individually to retrieved evidence — this granularity is what catches partial-accuracy failures (an answer that's mostly right with one unsupported detail) that whole-answer groundedness checks miss.
- An unpinned factoid signals either forbidden use of parametric memory or genuine hallucination, and contradictory evidence across retrieved sources should trigger an explicit refinement loop rather than a silent, arbitrary resolution.
- Token-level entropy is a real-time, in-process uncertainty signal — rising entropy during generation indicates the model's own confidence is dropping, and can flag or abort a likely-hallucinated claim before it's even fully generated, complementing after-the-fact factoid checking rather than replacing it.
