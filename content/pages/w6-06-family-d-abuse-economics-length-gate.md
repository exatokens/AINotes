---
id: w6-06-family-d-abuse-economics-length-gate
title: "Family D — Abuse, Economics, and the Cheapest Structural Gate"
week: 6
topic: "Act I: The Gatehouse — Keeping Bad Questions Out"
order: 6
summary: The last request-side family needs no forbidden word at all — it abuses the system by using it too much, spending its wallet, or exploiting its credulity — and one comparison operator, the length cap, retires most of it before a single classifier runs.
---

Not every threat needs a bad word. Some threats just need volume, or a sentence that quietly assumes something false.

## Core intuition

The cheapest attack is often the least malicious-looking: too many requests, an oversized prompt, or a question whose premise is built to mislead the model before any content safety check has a chance to fire.

## Why it matters

This family is about resource abuse and structural misuse, not semantic toxicity. It is the realization that the request path itself can be attacked even when the words seem harmless.

## Instructor framing

The loaded-question example deserves slower treatment than its brief space here suggests — it is the first appearance in the course of a genuinely graded response (reframing rather than refusing or answering at face value), and it previews Act III's entire discipline. Make sure students notice that the defense isn't "detect and block" the way earlier families worked; it's "detect and reframe," a qualitatively different move worth flagging explicitly.

## Worked example



Picture a script that discovers your public RAG endpoint and sends it a single request: a 50,000-word text pasted as the "question," asking the system to summarize, translate, and cross-reference it against the entire knowledge base. No profanity, no jailbreak phrasing, nothing a content classifier would flag — it's just enormous. That one request triggers a huge embedding call, a wide retrieval sweep, and a generation call with a maximal context window, at a cost potentially hundreds of times a normal query — this is the token bomb, denial of wallet in its purest form. A length cap set at, say, 500 tokens (comfortably above the enterprise-observed 95th percentile of under 50) rejects this request with a single integer comparison, before a single embedding is computed, at a cost of microseconds. The same 500-token ceiling happens to also catch the Trojan-paragraph attack, since burying an injected instruction in the middle of "a benign wall of text" requires exactly the kind of length a real question never needs.

This is the gatehouse as economics. A tiny structural rule — a cap on length or rate — can eliminate entire attack classes before the system ever calls a heavy model.

## Rate limiting and the token bomb

The cheapest member of Family D is **rate limiting** — the bouncer who counts heads before anyone checks IDs. It operates on metadata, not content, and costs a counter lookup: cap queries per user, per session, per IP, and globally, and return a clean `429` with `Retry-After` rather than silently dropping the request. A knowledge worker asks a handful of questions a minute; fifty a minute is not research, it is automation.

Its economic sibling counts tokens, because the distinctive LLM-era abuse is the **token bomb** — one request engineered to be catastrophically expensive to serve, what the industry honestly calls **denial of wallet**.

## The Trojan paragraph, and why length is its antidote

A hard ceiling on query length does double duty: a 500-token "query" is a document, not a question, and the same ceiling defeats the **Trojan-paragraph** injection — an instruction buried in the middle of a benign wall of text. A human skims the top and bottom and sees nothing wrong; the model reads the middle and obeys. The length cap kills the vehicle before the payload is ever tokenized, and it costs a single integer comparison — the cheapest defense in the entire chapter.

## The loaded question

The subtlest member of this family has no syntactic signature at all. *"Why did the CEO embezzle money in 2022?"* embeds a **presupposition** — that the CEO embezzled — and a naive system takes the query at face value: it retrieves documents about the CEO's finances, finds a routine audit report, and generates an answer that engages the premise, manufacturing AI-authored text that associates a named person with a crime that may never have happened. The harm is not in any flaggable token; it's in a proposition the sentence takes for granted.

The tools are an NLI check — does the corpus actually entail "the CEO embezzled money"? — or a presupposition extractor that surfaces the buried claim so it can be tested. The best response is usually not refusal but **reframing**: *"Based on available documents, there is no evidence that the CEO embezzled money; here is what the record does say about the CEO's finances."* This is the first appearance of the graded, honest partial that Act III will make into a discipline.

## The cheapest structural gate: query length and complexity bounds

One comparison operator can retire an entire attack class before any classifier reads a word. In enterprise search logs, the median query runs **8-15 tokens**; the 95th percentile sits **under 50**. A 500-token "question" is either a mistake or an attack — either way, the right first response is not to embed it.

Enforce it in three graded tiers, so the cap is a scalpel and not a cleaver:

| Tier | Threshold | Action | False-positive cost |
|---|---|---|---|
| Hard ceiling | ~500 tokens | reject outright, non-punitive message | essentially zero — no legitimate enterprise query needs to be this long |
| Soft warning | ~100 tokens | admit, but raise scrutiny downstream | low — long *and* injection-flagged is now two signals, not one |
| Structural complexity | deeply nested delimiters, several instructions separated by newlines/bullets, embedded code fences | flag for review | natural questions rarely have this morphology |

```python
# toy three-tier length/complexity gate
def gate(query: str):
    tokens = query.split()
    n = len(tokens)
    if n > 500:
        return "hard_reject", "exceeds maximum length; please shorten or split your question"
    flags = []
    if n > 100:
        flags.append("soft_warning: unusually long, raise downstream scrutiny")
    bullet_like = query.count("\n") + query.count("- ") + query.count("```")
    if bullet_like >= 3:
        flags.append("structural_complexity: multiple embedded instructions")
    return "admit", flags or ["clean"]

for q in ["What is our leave policy?", " ".join(["word"] * 150), "Do X\n- also do Y\n- also do Z\n```run this```"]:
    print(gate(q))
```

> Length and structure are syntactic tells — countable, reliable, near-free — and belong at the very front precisely because they clear the field cheaply for the semantic gates that cannot.






## Math explained step by step

Justify the specific threshold numbers (500 hard, 100 soft) using the stated percentile data, rather than treating them as arbitrary.

**Step 1 — start from the empirical query-length distribution.** The text reports enterprise search logs run median 8-15 tokens, with the 95th percentile under 50 tokens — meaning 95% of genuine, good-faith queries fall below 50 tokens, and the vast majority cluster far below that.

**Step 2 — set the hard ceiling using a large safety margin above the observed maximum, not the median.** 500 tokens is roughly 10x the 95th-percentile figure — a threshold this far above normal usage has a vanishingly small chance of rejecting a legitimate query (a false positive), because doing so would require a genuine question ten times longer than 95% of all real questions ever asked.

**Step 3 — set the soft-warning tier to catch the tail between "unusual but plausible" and "certainly not a normal question."** 100 tokens sits at roughly 2x the 95th percentile — high enough that few genuine questions land here, but not so high that a merely verbose, legitimate question about a complex multi-part policy gets hard-rejected. This tier trades a small increase in downstream scrutiny (not rejection) for catching a wider net of potential Trojan-paragraph or reconnaissance traffic.

**Step 4 — see why the three-tier structure, not a single cutoff, minimizes total error.** A single hard cutoff at 100 tokens would reject some legitimate long questions (a real false-positive cost); a single cutoff at 500 would miss more borderline abuse. The three-tier design (reject only far above normal, flag moderately above normal, and separately flag unusual structure) approximates a graded response to a graded risk, using only integer comparisons — no classifier, no embedding, and a false-positive rate this page describes as "essentially zero" at the hard tier specifically because of the 10x margin computed in Step 2.

## Practical pattern

Building the length/complexity gate as the first stage of a real gate stack:

1. measure your own query-length distribution before setting thresholds — the specific numbers here (8-15 median, sub-50 95th percentile) are one enterprise's data, and your own logs may differ meaningfully by domain (a legal research tool's normal queries may run longer than a customer-support bot's);
2. set the hard ceiling at a large multiple (8-10x) of your measured 95th percentile, not a round number chosen by intuition — this is what keeps the false-positive rate near zero while still catching genuinely anomalous requests;
3. implement the soft-warning and structural-complexity tiers as inputs to *downstream* scrutiny, not standalone rejections — a long query that also trips an injection classifier is a much stronger signal than either alone, and the tiered design exists specifically to compose with later, more expensive checks;
4. place this gate as literally the first check in your pipeline, before any embedding or tokenization for the main pipeline occurs — its entire value proposition is that it costs a single comparison and eliminates a meaningful fraction of both accidental and adversarial traffic before any expensive operation begins.

## Common traps

- setting length thresholds by intuition or copying a number from a blog post rather than measuring your own query-length distribution first — a threshold tuned for one domain's normal query length can be badly miscalibrated for another;
- treating the soft-warning tier as equivalent to the hard ceiling and rejecting on it directly, which discards the whole point of a graded tier system and risks real false positives on legitimate long questions;
- implementing the length check *after* other, more expensive checks (embedding, classification) rather than first, losing the entire cost-avoidance benefit that makes this the cheapest gate in the stack;
- treating the loaded-question defense as a binary detect-and-block problem like the other families, rather than recognizing it needs a qualitatively different response (reframing) — refusing outright wastes an opportunity to actually help the user, and answering at face value manufactures a harmful, unsupported association.

## Takeaways

- A simple length/complexity gate, calibrated against your own query-length distribution, can retire an entire class of resource-abuse and Trojan-paragraph attacks at the cost of a single integer comparison — the highest leverage-per-cost defense in the entire gatehouse.
- Loaded questions carry no syntactic attack signature at all — the harm lives in an unstated presupposition the query takes for granted, and the correct response is neither refusal nor face-value compliance, but reframing around what the evidence actually shows.
- Concretely: measure your own traffic's query-length percentiles before setting any threshold, then place the length gate as the literal first check in your pipeline — it should run before tokenization for the main retrieval path, not after.
