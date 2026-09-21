---
id: a7-07-patient-advocacy-agent-case-study
title: "The Patient Advocate: An Agent That Must Not Play Doctor"
week: 7
topic: "Act III: Designing Agents That Plan, Fail, and Reflect"
order: 7
summary: The patient-advocacy agent project forces every design pattern from this week — planning, tool calling, statefulness — through a single hard constraint: guide, never diagnose, using the SOAP framework as the structuring principle.
course: ai_agents
---

Every pattern covered so far this week — planning and execution, tool calling, the distinction between a stateless tool and a stateful agent — is easy to discuss in the abstract and easy to get subtly wrong in practice. The patient-advocacy project is useful precisely because it removes the abstraction: it's a single, concrete system with a rule so important that violating it isn't a quality bug, it's a legal and ethical failure. That constraint disciplines every architectural choice that follows it.

The project's motivation is not hypothetical. In regions where the physician-to-patient ratio can exceed 1:10,000, an accessible unit — camera, microphone, speaker — that helps a patient prepare a coherent case history before ever reaching a scarce physician is a genuine intervention, not a toy demo. But that same real-world stakes is exactly why the "do not play doctor" rule has to be architecturally enforced, not just stated as a guideline somewhere in a system prompt.

## Core intuition

The system's core job is captured by the medical SOAP framework — Subjective (the patient's own narrative, captured by voice, with medically relevant content filtered from noise), Objective (medically relevant data, including an image of the visible condition), Assessment (possible conditions, presented as candidate ICD codes with supporting evidence, explicitly *not* a diagnosis), and Plan (contextual next-step guidance — transportation, urgency, what to expect) — applied under one absolute constraint: the agent prepares a case history and advocates for the patient, it does not diagnose. The unauthorized practice of medicine is illegal, and beyond the legal risk, a system in this position, serving people with no other access to care, that gets a diagnosis wrong carries direct human cost.

This makes the agent's actual role closer to a remote nurse's assistant than to a doctor: gathering, structuring, and transmitting information faithfully, and producing two different outputs from the same underlying case history — a formal version (including the stored image) for the physician, and a plain-language version for the patient — rather than ever producing a single authoritative medical verdict itself.

## Why it matters

Every technical requirement in this project traces directly back to the "do not play doctor" constraint and the target user's real circumstances, which is worth making explicit because it shows how a single ethical constraint shapes concrete engineering decisions rather than staying abstract. The interface must be voice-only, because the target population is presumed to include people with limited literacy, and the course is explicit that illiteracy is not a handicap in a world with microphones and cameras — this isn't an accessibility nice-to-have, it's the actual condition that makes the system usable by its intended users at all. The system must support at least five languages with automatic language detection, with an ambitious goal of a hundred, because "frontier villages in the Global South" is not a linguistically homogeneous population and a system that only works in one language fails most of its actual target users.

Privacy gets a specific, concrete requirement rather than a general policy statement: the agent must explicitly request and receive permission before taking a picture — "permission-gated pictures" — because the Objective component of SOAP requires an image of a visible condition, and capturing that image without consent would be both an ethical violation and a trust-destroying design choice for a system whose entire value depends on vulnerable users trusting it enough to use it.

## Instructor framing

Teach this project as a worked demonstration of how a single hard constraint ("do not play doctor") propagates through every layer of system design — interface (voice-only), scope (Assessment as candidate ICD codes with evidence, never a diagnosis), output design (two audiences, two formats, from one case history), and privacy (explicit consent gating). Have students trace each requirement back to either the core constraint or the target population's real circumstances, rather than treating the requirements list as an arbitrary specification handed down — this is the difference between memorizing a feature list and understanding why each feature exists.

## Worked example

A patient in a remote village describes, in their own language, an itchy, spreading skin rash they've had for a week, mentioning in passing that their child was crying in the background and that they're worried about an upcoming trip. The Subjective-capture step must filter the medically relevant content (itching, duration, spreading pattern) from the irrelevant noise (the crying child, the trip) — this is itself a non-trivial reasoning task, requiring the agent to distinguish signal from conversational noise in unstructured spoken narrative, not just transcribe verbatim.

After requesting and receiving explicit permission, the agent captures an image of the affected skin — the Objective component. For Assessment, rather than saying "you have contact dermatitis," the agent must present a set of possible conditions consistent with the presenting symptoms and image, each with the specific supporting evidence for why it's plausible, framed explicitly as candidates for a physician's review, not a settled verdict. For Plan, the agent gives contextual next-step guidance appropriate to a remote setting — whether this warrants an urgent trip to the nearest facility or can reasonably wait, and what transportation and timing that implies given the patient's actual location — again framed as guidance, not a medical order. The final outputs split cleanly: a formal case history including the stored image goes to a remote physician for actual clinical judgment, while a separate, plain-language voice explanation goes to the patient describing what was found and what the recommended next step is, in language they can understand without medical training.

## Math explained step by step

Even a project this narrative-driven has a genuine quantifiable design question: how the system should weigh recall against precision in its Assessment step, given the asymmetric cost of the two error types in this specific context.

**Step 1 — define the two error types.** A **false negative** here means the Assessment step fails to include a genuinely relevant candidate condition among the possibilities it surfaces — potentially delaying appropriate care for something serious. A **false positive** means the Assessment step includes an implausible candidate condition alongside the genuinely relevant ones — adding noise to what the physician reviews, but not directly endangering the patient, since a physician's actual judgment is still the deciding factor before any treatment occurs.

**Step 2 — state the asymmetry explicitly.** Given the "do not play doctor" constraint and the population this system serves (limited access to physicians, meaning a missed urgent case may go unaddressed for a long time), the cost of a false negative — omitting a serious condition from consideration — is substantially higher than the cost of a false positive, since a physician downstream can filter out an implausible candidate quickly, but nothing downstream recovers a candidate that was never surfaced at all.

**Step 3 — the resulting design bias.** This asymmetry argues for tuning the Assessment step's recall higher than its precision — cast a wider net of candidate conditions with supporting evidence, accepting more noise for the physician to filter, rather than a narrower, higher-precision list that risks quietly dropping something serious. This is the same precision/recall trade-off structure from the very first week of retrieval theory, applied here to a specific, ethically-loaded context that dictates which side of the trade-off to favor.

**Step 4 — the constraint this doesn't relax.** Note carefully that favoring recall in the *Assessment* step (candidate generation) does not relax the "do not play doctor" constraint on the *Plan* step — even a wide, generous candidate list must still be framed as possibilities for physician review, and the Plan's guidance to the patient must stay in the register of "here's what to expect and how urgently to seek care," never "here's your diagnosis and treatment."

## Practical pattern

Building an agent under a hard, non-negotiable behavioral constraint like "do not play doctor":

1. identify the core constraint explicitly and trace every subsequent design decision back to it, rather than treating the constraint as one requirement among many equally-weighted ones — it should shape interface design, scope of output, and privacy handling, not just appear as a line in a system prompt;
2. design outputs for their actual downstream audience and use — a formal case history for a physician who will exercise real clinical judgment, versus plain-language guidance for a patient who needs to understand next steps, not a diagnosis; never collapse these into one output serving both audiences with the same content and framing;
3. gate any sensitive data capture (images, in this case) behind explicit, real consent at the point of capture, not a blanket consent obtained once at account setup — "permission-gated pictures" as a per-instance requirement, not a one-time checkbox;
4. bias generative steps toward recall over precision specifically where the asymmetric cost of a false negative is severe and unrecoverable downstream, and be explicit about why that bias is appropriate for this specific step, since the same bias would be wrong in a different context with a different cost asymmetry;
5. build the interface around the actual target population's real constraints (language, literacy, connectivity) rather than around what's easiest to implement — voice-only and multi-language support here aren't optional polish, they're required for the system to reach the users it's meant to serve at all.

## Common traps

- treating "do not play doctor" as a disclaimer to append to output rather than a constraint that should shape the Assessment step's actual content (candidate conditions with evidence, never a single authoritative diagnosis) and the Plan step's framing (guidance, not medical orders);
- designing a single output format serving both the physician and the patient, losing the appropriate register and detail level each audience actually needs;
- treating voice-only interface and multi-language support as accessibility features to add later if time permits, rather than core requirements without which the system fails its actual target population from the start;
- optimizing the Assessment step for precision (a short, clean list of likely conditions) without recognizing that the cost asymmetry in this specific context — a missed serious condition versus a noisy but harmless extra candidate — argues for the opposite bias toward recall.

## Takeaways

- The patient-advocacy project applies the SOAP framework (Subjective, Objective, Assessment, Plan) under one absolute constraint — advocate and guide, never diagnose — and that constraint should be traceable through every design decision: interface, output format, and privacy handling, not confined to a disclaimer.
- Designing two distinct outputs (formal case history for a physician, plain-language guidance for the patient) from one underlying case history respects that these are genuinely different audiences with different needs, rather than a single output serving both poorly.
- The Assessment step's precision/recall trade-off should be resolved by the asymmetric real-world cost of each error type — here, a missed serious condition (false negative) is far more costly than an implausible extra candidate a physician can quickly filter (false positive), which argues deliberately for a recall-biased design.
