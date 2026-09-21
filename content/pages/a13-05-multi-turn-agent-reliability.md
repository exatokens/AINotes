---
id: a13-05-multi-turn-agent-reliability
title: "The Multi-Turn Reliability Gap: Why Untrained Agents Fail 70% of the Time"
week: 13
topic: "Act I: Coordinating Many Minds"
order: 5
summary: A multi-step agentic task compounds per-step stochastic error rates multiplicatively, and this arithmetic — not any single dramatic bug — is why untrained agents attempting realistic workflows like flight booking succeed only about 30% of the time.
course: ai_agents
---

Ask an untrained agent to "book me a flight from New York to Paris under $800 next weekend," and a specific, sobering number shows up in practical experiments: roughly a 30% success rate. Not because the model doesn't understand the request, and not because any single component is dramatically broken — every individual step (checking a calendar, calling a search API, filtering results, selecting an option, executing a booking) can be individually quite reliable. The failure is not qualitative; it is arithmetic. This page derives that arithmetic precisely, catalogs the specific failure modes it produces, and explains why the standard remedies — more prompting, more supervised fine-tuning — hit a ceiling that only training-based approaches can break through.

## Core intuition

A single-turn LLM interaction — one input, one inference, one output — has an isolated, immediately-checkable success or failure. A genuinely agentic task is a **trajectory**: a sequential chain of interdependent steps, each involving either a deterministic tool call (checking a calendar, calling a search API — these execute reliably once invoked correctly) or a probabilistic LLM reasoning step (interpreting the date range, filtering results against a price constraint, deciding which option best matches the request — these are stochastic, not guaranteed correct even when the model is quite capable).

Even a high per-step LLM success rate compounds unfavorably across a multi-step trajectory, because trajectory-level success requires *every* step to succeed, and independent probabilities multiply.

## Why it matters

This reframes agent reliability engineering entirely. If a team observes a 30% end-to-end success rate and diagnoses it as "the model isn't good enough," the natural response is to reach for a bigger or more capable model — but the compounding math below shows that even a quite good per-step success rate produces a low trajectory-level success rate purely as a consequence of chaining enough steps together. The fix that actually addresses the *mechanism* of the failure is not (only) a smarter per-step model, but training specifically for reliable multi-step trajectories — which is precisely the motivation for the RL-based, trajectory-level training approaches covered in the rest of this week.

## Instructor framing

Walk through the three specific, catalogued failure modes before the mathematics, because they make the abstract "compounding probability" argument concrete and recognizable to anyone who has actually watched an agent fail in practice: **the Forgetful Agent** successfully executes early steps (finding dates) but loses track of an earlier constraint as context grows — booking a $950 flight despite an $800 limit stated at the very start, the constraint having effectively "faded" from the model's attention over the course of the trajectory (directly connected to the attention-decay and recitation material from Week 11). **The Indecisive Agent** fails to act autonomously at all, entering a confirmation loop — repeatedly asking the user for details already provided, rather than executing the task it was explicitly authorized to complete. **The Hallucinating Agent** is the most operationally dangerous: it claims success — "I have booked your ticket" — without ever having executed the underlying API call, satisfying the user conversationally while failing completely operationally, a gap between what the model *says* happened and what actually happened in the environment.

## Worked example

Walk the flight-booking task through its actual step sequence to see where compounding enters concretely: (1) a tool call to a calendar to resolve "next weekend" into specific dates — largely deterministic once correctly invoked; (2) a tool call to a search API (like Kayak) to retrieve available flights — deterministic; (3) an LLM reasoning step to filter the returned list against the $800 constraint — probabilistic, and exactly where the Forgetful Agent failure mode lives; (4) an LLM decision step selecting the best option among the filtered results — probabilistic; (5) a tool call to execute the booking — deterministic once correctly invoked, but exactly where the Hallucinating Agent failure mode lives if the LLM claims this step happened without actually triggering it. Even if the deterministic tool calls are essentially perfectly reliable, the two or three probabilistic LLM reasoning steps embedded in this five-step chain are enough, at realistic per-step reliability, to produce the observed ~30% end-to-end success rate — a number the course's own practical experiments arrived at directly, not a hypothetical worst case.

## Math explained step by step

Derive the compounding-probability arithmetic precisely, and calibrate it against the reported 30% figure.

**Step 1 — set up the compounding model.** If a task requires $k$ independent, sequential LLM reasoning steps, each succeeding with probability $p$, and the remaining deterministic tool-call steps succeed with probability near 1, the overall trajectory success probability is approximately $P(\text{success}) \approx p^k$.

**Step 2 — plug in a realistic per-step reliability.** At a quite respectable per-step reliability of $p = 0.95$ and $k = 5$ probabilistic reasoning steps embedded in the trajectory, $P(\text{success}) \approx 0.95^5 \approx 0.774$ — noticeably below 100% even at high per-step reliability, purely from the multiplication.

**Step 3 — see how quickly this degrades with either lower $p$ or higher $k$.** At $p = 0.85$ (a somewhat harder reasoning step, still reasonably capable) and $k = 8$ (a more realistic count once you include date resolution, constraint checking, multiple candidate evaluations, and confirmation logic), $P(\text{success}) \approx 0.85^8 \approx 0.272$ — closely matching the reported real-world ~30% figure for untrained agents attempting exactly this kind of task.

**Step 4 — the design implication this calibration supports.** Because $P(\text{success})$ is exponentially sensitive to both $p$ and $k$, there are exactly two independent levers for improving multi-turn reliability: reduce $k$ (simplify the trajectory — fewer, more consolidated reasoning steps, deterministic tool calls wherever a step can be made non-probabilistic) or increase $p$ (make each individual reasoning step more reliable, which prompting and SFT can partially achieve but which the next page's training-based approaches address more directly and durably, since they optimize for trajectory-level success rather than per-step imitation).

## Practical pattern

1. before attempting to fix a low agent success rate, measure $p$ (per-step reliability) and $k$ (number of probabilistic reasoning steps) for your specific trajectory — this tells you whether the leverage is in simplifying the trajectory or improving per-step reliability, and by how much each lever could plausibly help;
2. convert as many trajectory steps as possible from probabilistic (LLM reasoning) to deterministic (direct tool/API calls, rule-based logic) — every step converted removes one multiplicative factor from the compounding calculation entirely, rather than merely improving it;
3. build explicit verification steps into the trajectory specifically targeting the Hallucinating Agent failure mode — confirm that a claimed action (a booking, a database write) actually occurred in the environment before reporting success to the user, rather than trusting the model's own natural-language claim of completion;
4. apply Week 11's recitation pattern directly against the Forgetful Agent failure mode — periodically re-stating hard constraints (the $800 limit) later in the trajectory's context counteracts the attention decay that causes constraints stated early to be silently dropped by the time a late step needs them.

## Common traps

- diagnosing a low multi-step success rate as evidence the underlying model is insufficiently capable, when the compounding arithmetic shows that even quite reliable per-step performance produces low trajectory-level success once enough steps are chained;
- trusting an agent's own natural-language claim of task completion without independently verifying that the underlying action actually executed — the Hallucinating Agent failure mode is specifically about this gap between claimed and actual state;
- allowing hard constraints to be stated only once, early in a long trajectory, without any mechanism to keep them present in the model's effective attention through to the steps that need to respect them;
- attempting to fix multi-turn unreliability purely through more extensive prompting or more supervised fine-tuning data, both of which improve $p$ somewhat but do not directly train for trajectory-level, sequential-decision reliability the way trajectory-level RL training (covered in the next page) does.

## Takeaways

- Multi-step agentic tasks compound per-step success probabilities multiplicatively, so even quite reliable individual reasoning steps ($p \approx 0.85$–$0.95$) produce a much lower overall trajectory success rate once several such steps are chained — this arithmetic, not a single dramatic failure, explains the reported ~30% real-world success rate for untrained agents on realistic tasks like flight booking.
- The Forgetful Agent, the Indecisive Agent, and the Hallucinating Agent are three specific, recognizable failure patterns that this compounding produces in practice, each traceable to a different point in the trajectory.
- The two independent levers for improving reliability are reducing $k$ (fewer probabilistic steps, more deterministic tool calls) and increasing $p$ (more reliable individual reasoning steps) — diagnosing which lever has more available headroom in your specific system should precede any fix.
- Prompting and SFT can partially raise $p$, but neither directly optimizes for trajectory-level, sequential-decision success the way training approaches built specifically for multi-turn reliability can — motivating the Agent Lightning and GRPO-based material in the pages that follow.
